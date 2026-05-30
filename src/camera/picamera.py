"""RPi 카메라 프레임 소스 — Picamera2(libcamera) 기반.

WebcamSource와 동일한 인터페이스(read/release)를 제공해 run.py에서 교체 가능.
picamera2는 RPi OS 시스템 패키지로 제공되므로 venv 생성 시 --system-site-packages 필요할 수 있음.
무거운 import(picamera2, cv2)는 메서드 내부에 둔다.
"""
from __future__ import annotations


class PiCameraSource:
    """Picamera2로 RPi CSI 카메라 프레임을 읽는다."""

    def __init__(self, cfg: dict):
        """Args:
            cfg: config.yaml 의 camera 설정 (width, height, fps).
        """
        self.cfg = cfg
        # TODO: from picamera2 import Picamera2; 구성(configure)/시작(start).
        raise NotImplementedError("PiCameraSource 초기화 미구현")

    def read(self):
        """다음 프레임을 반환한다 (BGR ndarray). 실패 시 None."""
        # TODO: capture_array() 후 RGB->BGR 변환.
        raise NotImplementedError("PiCameraSource.read 미구현")

    def release(self) -> None:
        """카메라 리소스를 해제한다."""
        # TODO: picam2.stop()/close()
        raise NotImplementedError("PiCameraSource.release 미구현")
