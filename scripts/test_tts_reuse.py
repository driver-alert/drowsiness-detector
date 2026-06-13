"""pyttsx3 엔진 재사용 검증 (버전별 동작 확인용).

사용:
    python scripts/test_tts_reuse.py

하나의 엔진으로 say()/runAndWait()를 여러 번 호출해 두 번째 이후에도 실제로
발화하는지 확인한다. 정상 발화는 수 초가 걸리지만, 무음 버그가 나면 0.1초대로
즉시 반환된다 — 이를 기준으로 자동 판정한다.

pyttsx3 2.91 에서 정상이면, 챌린지 코드를 '엔진 재사용' 방식으로 되돌릴 수 있다.
"""
from __future__ import annotations

import time

import pyttsx3

PHRASES = ["첫 번째 발화입니다", "두 번째 발화입니다", "세 번째 발화입니다"]
SILENT_THRESHOLD = 0.5  # 이보다 빨리 끝나면 실제로 말하지 않은 것으로 간주


def main() -> None:
    print("pyttsx3 version:", getattr(pyttsx3, "__version__", "unknown"))

    engine = pyttsx3.init()
    engine.setProperty("rate", 170)

    durations = []
    for i, phrase in enumerate(PHRASES, 1):
        t0 = time.time()
        engine.say(phrase)
        engine.runAndWait()
        dt = round(time.time() - t0, 2)
        durations.append(dt)
        spoke = "발화함" if dt >= SILENT_THRESHOLD else "무음(버그)"
        print(f"[{i}] {phrase!r} -> {dt}s  {spoke}")

    ok = all(d >= SILENT_THRESHOLD for d in durations)
    print("\n결과:", "엔진 재사용 정상 (롤백 가능)" if ok else "두 번째 이후 무음 (재사용 불가)")


if __name__ == "__main__":
    main()
