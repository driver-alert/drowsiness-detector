"""PC 웹캠 프레임 소스 — OpenCV VideoCapture 기반.

무거운 import(cv2)는 메서드 내부에 둔다.
"""
from __future__ import annotations


class WebcamSource:
    """OpenCV VideoCapture로 PC 웹캠 프레임을 읽는다."""

    def __init__(self, cfg: dict):
        """Args:
            cfg: config.yaml 의 camera 설정 (width, height, fps).
        """
        import sys
        import cv2  # 무거운 import는 메서드 내부 (기존 스타일 유지)
        self.cfg = cfg
        # CAP_DSHOW: Windows에서 오픈 지연 완화 (Linux/RPi에서는 불필요)
        backend = cv2.CAP_DSHOW if sys.platform == "win32" else cv2.CAP_ANY
        self._cap = cv2.VideoCapture(0, backend)
        if not self._cap.isOpened():  # 오픈 실패 시 read()가 None을 반환하며 조용히 종료됨 — 명시적 예외로 대체
            raise RuntimeError("웹캠 열기 실패 — 카메라 연결을 확인하세요 (장치 0)")
        # config.yaml 의 camera 설정을 카메라에 반영
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH,  cfg["width"])
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg["height"])
        self._cap.set(cv2.CAP_PROP_FPS,          cfg["fps"])

    def read(self):
        """다음 프레임을 반환한다 (BGR ndarray). 실패 시 None."""
        ret, frame = self._cap.read()  # ret=성공 여부, frame=BGR ndarray
        return frame if ret else None  # 읽기 실패 시 None (메인 루프가 종료/스킵)

    def release(self) -> None:
        """카메라 리소스를 해제한다."""
        self._cap.release()  # 카메라 장치 점유 해제
