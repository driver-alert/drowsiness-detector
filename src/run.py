"""메인 루프 — 전체 흐름을 연결한다.

실행:
    python -m src.run --source webcam     # PC (웹캠 + 콘솔 경고)
    python -m src.run --source picamera   # RPi (CSI 카메라 + GPIO 경고)

카메라/경고 객체는 --source에 따라 주입받는다. 나머지 로직(vision/logic)은
하드웨어를 알지 못한다(스펙: 하드웨어 의존 코드 격리).
"""
from __future__ import annotations

import argparse
import time


def load_config(path: str = "config.yaml") -> dict:
    """config.yaml 을 읽어 설정 dict로 반환한다."""
    import yaml  # 무거운/외부 의존성은 함수 내부 import

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_source_and_alert(source: str, cfg: dict):
    """--source 에 맞는 (카메라, 경고) 객체를 생성해 반환한다.

    PC에서는 GPIO 코드를 호출하지 않는다(webcam -> ConsoleAlert).
    """
    if source == "webcam":
        from .camera.webcam import WebcamSource
        from .hardware.alert import ConsoleAlert
        return WebcamSource(cfg["camera"]), ConsoleAlert()
    elif source == "picamera":
        from .camera.picamera import PiCameraSource
        from .hardware.alert import GpioAlert
        return PiCameraSource(cfg["camera"]), GpioAlert(cfg["gpio"])
    raise ValueError(f"알 수 없는 source: {source}")


def main() -> None:
    parser = argparse.ArgumentParser(description="실시간 운전자 졸음 감지 시스템")
    parser.add_argument(
        "--source",
        choices=["webcam", "picamera"],
        required=True,
        help="프레임 입력 소스 (PC=webcam, RPi=picamera)",
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="설정 파일 경로 (기본: config.yaml)",
    )
    args = parser.parse_args()

    cfg = load_config(args.config)

    # 구성요소 조립 (의존성 주입)
    from .vision.landmarks import FaceLandmarker
    from .vision.ear import eye_aspect_ratio
    from .vision.head_pose import estimate_pitch
    from .logic.drowsiness import DrowsinessJudge
    from .logic.recorder import ClipRecorder
    from .logic.event_log import EventLogger

    camera, alert = build_source_and_alert(args.source, cfg)
    landmarker = FaceLandmarker(cfg["model"]["task_path"])
    judge = DrowsinessJudge(cfg)
    recorder = ClipRecorder(cfg["recorder"])
    logger = EventLogger(cfg["event_log"])

    # 웹 대시보드와 공유할 상태 (run.py가 갱신, Flask가 읽음)
    state = {"stage": "ok", "ear": None, "pitch": None, "ts": None}
    prev_stage = None  # 단계 전이 감지용

    # TODO: web/app.create_app(state, cfg["event_log"]["output_path"]) 를 별도 스레드로 띄우기.

    try:
        while True:
            frame = camera.read()
            if frame is None:
                break

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

            # --- Output: 경고 + (danger 시) 클립 저장 + 단계 전이 로그 ---
            alert.set_stage(stage)
            recorder.feed(frame)
            clip_path = recorder.save() if stage == "danger" else None
            if stage != prev_stage:
                logger.log(stage, vision, clip=clip_path)
            prev_stage = stage

            state.update(stage=stage, **vision)
    except KeyboardInterrupt:
        pass
    finally:
        camera.release()
        alert.close()


if __name__ == "__main__":
    main()
