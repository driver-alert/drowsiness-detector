"""산수 챌린지 독립 실행 테스트 (PC).

사용 (프로젝트 루트에서):
    python scripts/test_challenge.py

config.yaml 의 challenge 설정으로 ArithmeticChallenge 를 1회 실행한다.
TTS로 두 자리 산수 문제가 출제되면 마이크에 답을 말한다.
정답/응답시간 결과가 콘솔에 출력된다. (pyttsx3 / SpeechRecognition / PyAudio 필요)
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    import yaml

    from src.logic.challenge import ArithmeticChallenge

    with open("config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    ch = ArithmeticChallenge(cfg["challenge"])
    
    # 마이크 없이도 확인 가능한 숫자 파싱 점검
    assert ch._parse_number("92") == 92
    assert ch._parse_number("정답은 92입니다") == 92
    assert ch._parse_number("팔") == 8
    assert ch._parse_number("모르겠어요") is None
    print("[TEST] _parse_number 통과")

    print("[TEST] 문제를 듣고 마이크에 답을 말하세요...")
    result = ch.run()
    print("[TEST] 결과:", result)


if __name__ == "__main__":
    main()
