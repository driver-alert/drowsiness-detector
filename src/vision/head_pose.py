"""머리 자세(Head Pose) 추정 — solvePnP로 Pitch(고개 숙임) 계산.

고개를 아래로 떨구는 동작을 졸음의 보조 신호로 사용한다.
"""
from __future__ import annotations

import numpy as np
import cv2

# 일반 얼굴 3D 모델점(mm), OpenCV Y-down 기준 (아래=양수, 위=음수)
# 원래 Y-up 모델의 Y값을 반전: chin(아래)→양수, eye(위)→음수
MODEL_3D = np.array([
    (0, 0, 0),          # 코끝
    (0, 330, -65),      # 턱 (코 아래 → +Y)
    (-225, -170, -135), # 좌안 바깥끝 (코 위 → -Y)
    (225, -170, -135),  # 우안 바깥끝
    (-150, 150, -125),  # 좌측 입꼬리 (코 아래 → +Y)
    (150, 150, -125),   # 우측 입꼬리
], dtype=np.float64)
IDX = [1, 152, 33, 263, 61, 291]  # MODEL_3D와 같은 순서의 MediaPipe 인덱스


def estimate_pitch(landmarks, frame_size) -> float:
    """얼굴 랜드마크로부터 머리 pitch 각도(degree)를 계산한다.

    Args:
        landmarks: FaceLandmarker가 반환한 468점 랜드마크.
        frame_size: (width, height) 픽셀 크기 — 카메라 내부 파라미터 추정용.

    Returns:
        pitch 각도(degree). 양수=고개 숙임 방향(프로젝트 컨벤션은 구현 시 고정).
    """
    w, h = frame_size
    # 정규화 좌표 → 픽셀 좌표 (solvePnP는 픽셀 단위 2D점 필요)
    pts2d = np.array([[landmarks[i].x*w, landmarks[i].y*h] for i in IDX], dtype=np.float64)
    # 카메라 내부 파라미터 추정: 초점거리≈영상 폭, 주점=영상 중심
    cam = np.array([[w, 0, w/2], [0, w, h/2], [0, 0, 1]], dtype=np.float64)
    dist = np.zeros((4, 1))  # 렌즈 왜곡 무시 (보정값 없음)
    # 3D-2D 대응으로 머리 회전(rvec)·이동(tvec) 추정
    ok, rvec, tvec = cv2.solvePnP(MODEL_3D, pts2d, cam, dist, flags=cv2.SOLVEPNP_ITERATIVE)
    if not ok:  # 랜드마크 배치가 비정상일 때 수렴 실패 — 크래시 방지
        return 0.0
    R, _ = cv2.Rodrigues(rvec)  # 회전벡터 → 회전행렬
    pitch = np.degrees(np.arctan2(-R[2, 1], R[2, 2]))  # x축 회전각 추출 → pitch(deg)
    return float(pitch)  # 고개 숙임 = 양수
