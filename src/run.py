"""메인 루프: 졸음 감지 시스템의 전체 흐름을 연결한다.

실행:
    python -m src.run
    python -m src.run --config custom.yaml

카메라와 경고 출력 객체는 실행 플랫폼에 맞춰 선택한다.
나머지 비전/판단 로직은 하드웨어 세부사항에 의존하지 않는다.
"""
from __future__ import annotations

import argparse
import sys
import threading
import time


def load_config(path: str = "config.yaml") -> dict:
    """config.yaml을 읽어 설정 dict로 반환한다."""
    import yaml

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_source_and_alert(cfg: dict):
    """현재 플랫폼에 맞는 카메라와 경고 객체를 생성한다.

    Windows: ConsoleAlert / RPi(Linux): GpioAlert
    """
    from .camera.webcam import WebcamSource

    if sys.platform == "win32":
        from .hardware.alert import ConsoleAlert

        return WebcamSource(cfg["camera"]), ConsoleAlert()

    from .hardware.alert import GpioAlert

    return WebcamSource(cfg["camera"]), GpioAlert(cfg["gpio"])


def start_dashboard(state: dict, cfg: dict, frame_store: dict) -> threading.Thread:
    """Flask 대시보드를 백그라운드 스레드로 실행한다."""
    from .web.app import create_app

    web_cfg = cfg["web"]
    app = create_app(state, cfg["event_log"]["output_path"], frame_store)
    thread = threading.Thread(
        target=app.run,
        kwargs={
            "host": web_cfg["host"],
            "port": int(web_cfg["port"]),
            "debug": False,
            "use_reloader": False,
            "threaded": True,
        },
        daemon=True,
        name="dashboard",
    )
    thread.start()
    print(f"[WEB] Dashboard: http://127.0.0.1:{web_cfg['port']} (bind: {web_cfg['host']})")
    return thread


def update_frame_store(frame_store: dict, frame, label: str | None = None) -> None:
    """Encode the latest camera frame as JPEG for the Flask /video stream."""
    import cv2

    preview = frame.copy()
    if label:
        cv2.rectangle(preview, (0, 0), (preview.shape[1], 38), (0, 0, 0), -1)
        cv2.putText(preview, label, (12, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    ok, encoded = cv2.imencode(".jpg", preview, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
    if not ok:
        return

    with frame_store["lock"]:
        frame_store["jpeg"] = encoded.tobytes()
        frame_store["updated"] = time.time()


def main() -> None:
    parser = argparse.ArgumentParser(description="실시간 운전자 졸음 감지 시스템")
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="설정 파일 경로 (기본: config.yaml)",
    )
    args = parser.parse_args()

    cfg = load_config(args.config)

    # 구성요소 조립: 하드웨어 의존 객체를 메인 루프에 주입한다.
    from .logic.challenge import ChallengeManager
    from .logic.drowsiness import DrowsinessJudge
    from .logic.event_log import EventLogger
    from .logic.recorder import ClipRecorder
    from .vision.ear import eye_aspect_ratio
    from .vision.head_pose import estimate_pitch
    from .vision.landmarks import FaceLandmarker

    camera, alert = build_source_and_alert(cfg)
    landmarker = FaceLandmarker(cfg["model"]["task_path"])
    judge = DrowsinessJudge(cfg)
    recorder = ClipRecorder(cfg["recorder"])
    logger = EventLogger(cfg["event_log"])
    challenge_manager = ChallengeManager(cfg)

    # Flask 대시보드와 공유할 상태.
    state = {"stage": "ok", "ear": None, "pitch": None, "ts": None}
    frame_store = {"jpeg": None, "updated": None, "lock": threading.Lock()}
    prev_stage = None

    start_dashboard(state, cfg, frame_store)

    try:
        while True:
            frame = camera.read()
            if frame is None:
                break
            update_frame_store(frame_store, frame, "detecting")

            # --- Vision: 프레임 -> {ear, pitch, ts} ---
            landmarks = landmarker.detect(frame)
            if landmarks is None:
                continue

            h, w = frame.shape[:2]
            vision = {
                "ear": eye_aspect_ratio(landmarks),
                "pitch": estimate_pitch(landmarks, (w, h)),
                "ts": time.time(),
            }

            # --- Logic: 단계 판단 ---
            stage = judge.update(vision)
            update_frame_store(
                frame_store,
                frame,
                f"{stage.upper()}  EAR={vision['ear']:.3f}  PITCH={vision['pitch']:.1f}",
            )

            # --- Output: 경고 + 클립 저장 + 단계 전이 로그 ---
            alert.set_stage(stage)
            recorder.feed(frame)
            clip_path = recorder.save() if stage == "danger" else None
            if stage != prev_stage:
                logger.log(stage, vision, clip=clip_path)
                if stage == "danger":
                    challenge_manager.on_danger(vision["ts"])
            prev_stage = stage

            state.update(stage=stage, **vision)
    except KeyboardInterrupt:
        pass
    finally:
        camera.release()
        recorder.close()
        alert.close()


if __name__ == "__main__":
    main()
