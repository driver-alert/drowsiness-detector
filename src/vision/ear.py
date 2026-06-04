"""EAR(Eye Aspect Ratio) 계산.

눈의 세로/가로 비율로 눈 감김 정도를 수치화한다. 값이 작을수록 눈이 감긴 상태.
"""
from __future__ import annotations

import numpy as np

# MediaPipe 468점 중 눈 6점 인덱스 (순서: p1 가로끝, p2·p3 위, p4 가로끝, p5·p6 아래)
LEFT  = [33, 160, 158, 133, 153, 144]
RIGHT = [362, 385, 387, 263, 373, 380]


def _ear_one(landmarks, idx) -> float:
    """한쪽 눈의 EAR. p[0]~p[5] = 위 인덱스 6점."""
    p = [np.array([landmarks[i].x, landmarks[i].y]) for i in idx]  # 정규화 (x, y)
    vert  = np.linalg.norm(p[1]-p[5]) + np.linalg.norm(p[2]-p[4])  # 세로 두 쌍 합
    horiz = 2.0 * np.linalg.norm(p[0]-p[3])                        # 가로 거리 ×2
    if horiz < 1e-6:  # 비정상 랜드마크로 가로 거리가 0에 가까울 때 inf/nan 방지
        return 0.0
    return float(vert / horiz)  # 눈 감을수록 작아짐


def eye_aspect_ratio(landmarks) -> float:
    """양쪽 눈 EAR의 평균을 계산한다.

    Args:
        landmarks: FaceLandmarker가 반환한 468점 랜드마크.

    Returns:
        좌·우 눈 EAR의 평균값.
    """
    return (_ear_one(landmarks, LEFT) + _ear_one(landmarks, RIGHT)) / 2.0  # 좌우 평균
