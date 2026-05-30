"""MediaPipe Tasks API Face Landmarker 래퍼.

구형 Face Mesh 솔루션 API가 아니라 **Tasks API의 FaceLandmarker**를 사용한다.
468점 얼굴 랜드마크를 제공한다.

무거운 import(mediapipe)는 모듈 최상단이 아니라 메서드 내부에 둔다 —
패키지 미설치 상태에서도 이 모듈을 import할 수 있게 하기 위함.
"""
from __future__ import annotations


class FaceLandmarker:
    """`.task` 모델을 로드해 프레임에서 얼굴 랜드마크를 추출한다."""

    def __init__(self, task_path: str):
        """Args:
            task_path: Face Landmarker `.task` 모델 파일 경로 (config.model.task_path).
        """
        self.task_path = task_path
        # TODO: mediapipe.tasks.python.vision.FaceLandmarker 를 task_path로 초기화.
        #   from mediapipe.tasks import python
        #   from mediapipe.tasks.python import vision
        raise NotImplementedError("FaceLandmarker 초기화 미구현")

    def detect(self, frame):
        """BGR 프레임에서 얼굴 랜드마크를 추출한다.

        Args:
            frame: OpenCV BGR ndarray.

        Returns:
            468개 (x, y, z) 랜드마크 시퀀스. 얼굴 미검출 시 None.
        """
        # TODO: BGR -> RGB 변환 후 mp.Image 생성, self._landmarker.detect(...) 호출.
        raise NotImplementedError("landmark detect 미구현")
