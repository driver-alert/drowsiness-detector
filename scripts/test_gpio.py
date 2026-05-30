"""GPIO 점등·소리 테스트 (RPi 전용).

사용 (RPi에서):
    python scripts/test_gpio.py

config.yaml 의 gpio 핀 번호로 LED(녹/황/적)와 부저를 순차 점등/소리 테스트한다.
gpiozero import는 main 내부 — PC에서 import만 해도 깨지지 않게.
"""
from __future__ import annotations


def main() -> None:
    import yaml
    # import time
    # from gpiozero import LED, Buzzer  # RPi에서만 동작

    with open("config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    pins = cfg["gpio"]
    print("GPIO 핀 설정:", pins)

    # TODO: 각 LED를 time.sleep(1) 간격으로 차례 점등, 부저 짧게/길게 울려 배선 확인.
    raise NotImplementedError("GPIO 테스트 미구현")


if __name__ == "__main__":
    main()
