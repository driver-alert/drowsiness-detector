"""EAR(Eye Aspect Ratio) 계산.

눈의 세로/가로 비율로 눈 감김 정도를 수치화한다. 값이 작을수록 눈이 감긴 상태.
"""
from __future__ import annotations


def eye_aspect_ratio(landmarks) -> float:
    """양쪽 눈 EAR의 평균을 계산한다.

    Args:
        landmarks: FaceLandmarker가 반환한 468점 랜드마크.

    Returns:
        좌·우 눈 EAR의 평균값.
    """
    # TODO: MediaPipe 468점 인덱스로 좌/우 눈 6점을 골라
    #   EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||) 계산 후 평균.
    raise NotImplementedError("EAR 계산 미구현")
