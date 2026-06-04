"""vision 파이프라인 통합 검증 스크립트 (Step 6 검증용, 확인 후 삭제 가능).

실행: python scripts/test_vision.py  (프로젝트 루트에서)

확인 항목:
  - 웹캠 + FaceLandmarker 정상 동작 여부
  - EAR: 눈 뜸↑ vs 감음↓ 값 변화 확인 (ear.threshold 튜닝용)
  - Pitch: 정면≈0°, 고개 숙임 시 양수 증가 확인 (pitch_threshold 튜닝용)
  - Windows: ESC 키로 종료 / RPi: Ctrl+C로 종료
"""
from __future__ import annotations

import sys
import time

from src.run import load_config
from src.camera.webcam import WebcamSource
from src.vision.landmarks import FaceLandmarker
from src.vision.ear import eye_aspect_ratio
from src.vision.head_pose import estimate_pitch

GUI = sys.platform == "win32"
if GUI:
    import cv2

cfg = load_config()
cam = WebcamSource(cfg["camera"])
lm = FaceLandmarker(cfg["model"]["task_path"])

print("vision test start -", "press ESC to quit" if GUI else "Ctrl+C to quit")
try:
    while True:
        frame = cam.read()
        if frame is None:
            break
        L = lm.detect(frame)
        if L is None:
            if GUI:
                # 얼굴 미검출 프레임은 그냥 표시만
                cv2.imshow("vision", frame)
                if cv2.waitKey(1) == 27:
                    break
            continue

        h, w = frame.shape[:2]
        ear   = round(eye_aspect_ratio(L), 3)
        pitch = round(estimate_pitch(L, (w, h)), 1)
        print({"ear": ear, "pitch": pitch, "ts": round(time.time(), 1)})

        if GUI:
            cv2.putText(frame, f"EAR={ear}  PITCH={pitch}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("vision", frame)
            if cv2.waitKey(1) == 27:
                break
except KeyboardInterrupt:
    pass

cam.release()
if GUI:
    cv2.destroyAllWindows()
