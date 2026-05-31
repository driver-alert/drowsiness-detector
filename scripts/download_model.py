"""MediaPipe Face Landmarker `.task` 모델 다운로드.

사용:
    python scripts/download_model.py

models/face_landmarker.task 가 없으면 MediaPipe 공식 모델을 내려받아 저장한다.
(.task 파일은 용량이 커 git에 포함하지 않는다 — .gitignore 참고.)
"""
from __future__ import annotations

import urllib.request
from pathlib import Path

# MediaPipe 공식 Face Landmarker 모델 URL (구현 시 최신 경로 확인).
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
    "face_landmarker/float16/1/face_landmarker.task"
)
DEST = Path("models/face_landmarker.task")


def main() -> None:
    DEST.parent.mkdir(parents=True, exist_ok=True)
    if DEST.exists():
        print(f"이미 존재: {DEST}")
        return
    try:
        print(f"다운로드 중: {MODEL_URL}")
        urllib.request.urlretrieve(MODEL_URL, DEST)
        print(f"저장 완료: {DEST} ({DEST.stat().st_size} bytes)")
    except Exception:
        if DEST.exists():
            DEST.unlink()      # 부분 파일 정리
        raise


if __name__ == "__main__":
    main()
