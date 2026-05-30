"""이벤트 영상 클립 저장 — danger 단계 발생 시 최근 프레임을 mp4로 기록.

OpenCV VideoWriter 사용. 무거운 import(cv2)는 메서드 내부에 둔다.
"""
from __future__ import annotations


class ClipRecorder:
    """롤링 버퍼에 프레임을 쌓아두고, danger 시점 전후를 클립으로 저장한다."""

    def __init__(self, cfg: dict):
        """Args:
            cfg: config.yaml 의 recorder 설정 (output_dir, pre_seconds, post_seconds).
        """
        self.cfg = cfg
        # TODO: 링 버퍼(collections.deque) 준비, output_dir 생성.
        raise NotImplementedError("ClipRecorder 초기화 미구현")

    def feed(self, frame):
        """매 프레임 호출 — 롤링 버퍼에 프레임을 추가한다."""
        # TODO: deque에 frame append (pre_seconds 분량 유지).
        raise NotImplementedError("recorder.feed 미구현")

    def save(self) -> str:
        """현재 버퍼 + 이후 post_seconds 프레임을 mp4로 저장하고 경로를 반환한다."""
        # TODO: cv2.VideoWriter로 output_dir/<timestamp>.mp4 작성.
        raise NotImplementedError("recorder.save 미구현")
