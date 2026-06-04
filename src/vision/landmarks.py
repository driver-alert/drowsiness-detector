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
        # Tasks API 관련 import는 메서드 내부 (미설치 상태에서도 모듈 import 가능)
        import mediapipe as mp
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision
        self.task_path = task_path
        self._mp = mp  # detect()에서 mp.Image 생성에 재사용
        options = vision.FaceLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=task_path),  # .task 모델 로드
            running_mode=vision.RunningMode.IMAGE,  # 프레임마다 독립 추론 (detect 시그니처와 일치)
            num_faces=1,                            # 운전자 1명만 추적
        )
        self._landmarker = vision.FaceLandmarker.create_from_options(options)

    def detect(self, frame):
        """BGR 프레임에서 얼굴 랜드마크를 추출한다.

        Args:
            frame: OpenCV BGR ndarray.

        Returns:
            468개 (x, y, z) 랜드마크 시퀀스. 얼굴 미검출 시 None.
        """
        import cv2
        # MediaPipe는 RGB 입력 — BGR(OpenCV) → RGB 변환 필수 (누락 시 검출률 급락)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = self._mp.Image(image_format=self._mp.ImageFormat.SRGB, data=rgb)
        result = self._landmarker.detect(mp_image)
        if not result.face_landmarks:   # 얼굴 미검출
            return None                 # 메인 루프가 이 프레임을 continue로 건너뜀
        return result.face_landmarks[0]  # 첫 얼굴의 468점 NormalizedLandmark 리스트
