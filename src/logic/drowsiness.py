"""졸음 3단계 판단 로직.

입력  : vision = {"ear": float, "pitch": float, "ts": float}
출력  : 단계 문자열 "ok" / "warn" / "danger"

방식(프레임 카운팅):
  - 눈 감음(EAR < threshold) 또는 고개 숙임(pitch > pitch_threshold)이면
    "졸음 의심 프레임"으로 보고 연속 카운터를 +1.
  - 정상 프레임이 오면 카운터를 0으로 리셋.
  - 연속 카운터가 danger_frames 이상 -> danger
                     warn_frames   이상 -> warn
                     그 외               -> ok
"""
from __future__ import annotations


class DrowsinessJudge:
    def __init__(self, cfg: dict):
        ear_cfg = cfg["ear"]
        self.ear_threshold = float(ear_cfg["threshold"])
        self.warn_frames = int(ear_cfg["warn_frames"])
        self.danger_frames = int(ear_cfg["danger_frames"])
        self.pitch_threshold = float(cfg["head_pose"]["pitch_threshold"])

        self._count = 0  # 연속 졸음 의심 프레임 수

    def _is_drowsy(self, ear, pitch) -> bool:
        eyes_closed = ear is not None and ear < self.ear_threshold
        head_down = pitch is not None and pitch > self.pitch_threshold
        return eyes_closed or head_down

    def update(self, vision: dict) -> str:
        if self._is_drowsy(vision.get("ear"), vision.get("pitch")):
            self._count += 1
        else:
            self._count = 0

        if self._count >= self.danger_frames:
            return "danger"
        if self._count >= self.warn_frames:
            return "warn"
        return "ok"