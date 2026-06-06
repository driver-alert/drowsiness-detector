"""졸음 이벤트 로그 — 단계 전이를 JSON 파일로 기록."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


def _num(x):
    """numpy 타입 등을 일반 float로 변환 (JSON 저장 안전용)."""
    return float(x) if x is not None else None


class EventLogger:
    def __init__(self, cfg: dict):
        self.output_path = cfg["output_path"]
        self.log_stages = cfg["log_stages"]
        # 로그 파일이 들어갈 폴더 보장 (없으면 생성)
        Path(self.output_path).parent.mkdir(parents=True, exist_ok=True)

    def log(self, stage: str, vision: dict, clip: str | None = None) -> None:
        # 1) 기록 대상 단계가 아니면 무시
        if stage not in self.log_stages:
            return

        # 2) 이벤트 한 건 구성
        entry = {
            "ts": vision["ts"],
            "time": datetime.now().isoformat(timespec="seconds"),
            "stage": stage,
            "ear": _num(vision["ear"]),
            "pitch": _num(vision["pitch"]),
            "clip": clip,
        }

        # 3) 기존 JSON 배열을 읽어 append 후 다시 저장 (파일 없으면 []에서 시작)
        path = Path(self.output_path)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, list):
                data = []
        except (FileNotFoundError, json.JSONDecodeError):
            data = []

        data.append(entry)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")