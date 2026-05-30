"""머리 자세(Head Pose) 추정 — solvePnP로 Pitch(고개 숙임) 계산.

고개를 아래로 떨구는 동작을 졸음의 보조 신호로 사용한다.
"""
from __future__ import annotations


def estimate_pitch(landmarks, frame_size) -> float:
    """얼굴 랜드마크로부터 머리 pitch 각도(degree)를 계산한다.

    Args:
        landmarks: FaceLandmarker가 반환한 468점 랜드마크.
        frame_size: (width, height) 픽셀 크기 — 카메라 내부 파라미터 추정용.

    Returns:
        pitch 각도(degree). 양수=고개 숙임 방향(프로젝트 컨벤션은 구현 시 고정).
    """
    # TODO: 3D 기준 모델점 + 2D 랜드마크 대응점으로 cv2.solvePnP 호출,
    #   회전벡터 -> 오일러각 변환해 pitch 추출.
    raise NotImplementedError("head pose pitch 계산 미구현")
