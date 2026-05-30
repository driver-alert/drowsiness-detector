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
        self.cfg = cfg
        # TODO: import cv2; cv2.VideoCapture(0) 열고 width/height/fps 설정.
        raise NotImplementedError("WebcamSource 초기화 미구현")

    def read(self):
        """다음 프레임을 반환한다 (BGR ndarray). 실패 시 None."""
        # TODO: ret, frame = cap.read(); 실패 시 None.
        raise NotImplementedError("WebcamSource.read 미구현")

    def release(self) -> None:
        """카메라 리소스를 해제한다."""
        # TODO: cap.release()
        raise NotImplementedError("WebcamSource.release 미구현")
