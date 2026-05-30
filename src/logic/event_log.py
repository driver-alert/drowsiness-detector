"""졸음 이벤트 로그 — 단계 전이를 JSON 파일로 기록.

제안서 결과물의 '이벤트 로그'에 해당. 사후 운전 패턴 분석과 대시보드 표시에 사용한다.
단계 전이(전이 판정은 run.py 책임)마다 1건을 받아 JSON 배열 파일에 추가하는 단순 sink.
무거운 의존성 없음(stdlib json/datetime).
"""
from __future__ import annotations


class EventLogger:
    """이벤트 1건을 받아 JSON 배열 파일(output_path)에 누적 기록한다."""

    def __init__(self, cfg: dict):
        """Args:
            cfg: config.yaml 의 event_log 설정.
                output_path: JSON 로그 파일 경로 (예: logs/events.json).
                log_stages: 기록 대상 단계 목록 (예: ["ok", "warn", "danger"]).
        """
        self.output_path = cfg["output_path"]
        self.log_stages = cfg["log_stages"]
        # TODO: Path(output_path).parent.mkdir(parents=True, exist_ok=True) 로 디렉터리 보장.

    def log(self, stage: str, vision: dict, clip: str | None = None) -> None:
        """한 건의 단계 전이 이벤트를 기록한다.

        Args:
            stage: 전이한 단계 ("ok"/"warn"/"danger").
            vision: {"ear": float, "pitch": float, "ts": float}.
            clip: danger 시 ClipRecorder.save()가 반환한 클립 경로, 그 외 None.

        엔트리 스키마:
            {"ts": float, "time": ISO8601, "stage": str,
             "ear": float, "pitch": float, "clip": str|None}
        """
        # TODO:
        #   1) stage not in self.log_stages 이면 무시(return).
        #   2) entry = {"ts": vision["ts"],
        #               "time": datetime.now().isoformat(timespec="seconds"),
        #               "stage": stage, "ear": vision["ear"],
        #               "pitch": vision["pitch"], "clip": clip}
        #   3) output_path JSON 배열을 read-modify-write 로 append
        #      (파일 없으면 []에서 시작). 전이는 저빈도라 충분.
        #      쓰기가 잦아 부담되면 JSON Lines(.jsonl, 한 줄=한 객체) 로 전환 가능.
        raise NotImplementedError("이벤트 로그 기록 미구현")
