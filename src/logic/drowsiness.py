"""졸음 3단계 판단 — 프레임 카운팅 기반.

Vision 출력(dict: ear, pitch, ts)을 받아 연속 프레임 수를 누적해
"ok" / "warn" / "danger" 단계를 반환한다.
"""
from __future__ import annotations


class DrowsinessJudge:
    """EAR/pitch 임계값과 연속 프레임 수로 졸음 단계를 판단한다."""

    def __init__(self, cfg: dict):
        """Args:
            cfg: config.yaml 의 설정 dict (ear.threshold, ear.warn_frames,
                ear.danger_frames, head_pose.pitch_threshold 등).
        """
        self.cfg = cfg
        self._closed_frames = 0  # 눈 감김 연속 프레임 카운터
        # TODO: cfg에서 임계값/프레임 기준 읽어 보관.
        raise NotImplementedError("DrowsinessJudge 초기화 미구현")

    def update(self, vision: dict) -> str:
        """한 프레임의 vision 결과로 단계를 갱신해 반환한다.

        Args:
            vision: {"ear": float, "pitch": float, "ts": float}.

        Returns:
            "ok" | "warn" | "danger".
        """
        # TODO: ear < threshold 이면 카운터 증가, 아니면 리셋.
        #   카운터가 danger_frames 이상 -> "danger",
        #   warn_frames 이상 -> "warn", 그 외 -> "ok".
        #   pitch_threshold 초과 시 보조 가중.
        raise NotImplementedError("졸음 단계 판단 미구현")
