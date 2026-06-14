import cv2
import numpy as np
import os
import json
import time

def run_test():
    print("--- PR 전 최종 기능 검증 시작 ---")
    
    # 1. 가짜 영상 파일 생성 (H.264 시도)
    os.makedirs("clips", exist_ok=True)
    filename = f"test_clip_{int(time.time())}.mp4"
    path = os.path.join("clips", filename)
    
    fourcc = cv2.VideoWriter_fourcc(*"avc1")
    out = cv2.VideoWriter(path, fourcc, 20.0, (640, 480))
    for i in range(60):
        img = np.zeros((480, 640, 3), np.uint8)
        cv2.putText(img, f"TEST CLIP: FRAME {i}", (100, 240), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
        out.write(img)
    out.release()
    print(f"[OK] 테스트용 영상 생성 완료: {path}")

    # 2. 가짜 로그 데이터 생성
    os.makedirs("logs", exist_ok=True)
    log_path = "logs/events.json"
    entry = {
        "ts": time.time(),
        "time": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "stage": "danger",
        "ear": 0.12,
        "pitch": 25.0,
        "clip": path.replace("\\", "/") # 윈도우 경로 대응
    }
    
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump([entry], f, indent=2, ensure_ascii=False)
    print(f"[OK] 테스트용 로그 작성 완료: {log_path}")
    print("\n이제 Flask를 실행하고 브라우저(localhost:5000)에서 '재생' 버튼을 눌러보세요!")

if __name__ == "__main__":
    run_test()