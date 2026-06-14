"""GPIO 점등·소리 테스트 (RPi 전용).

사용 (RPi에서):
    python scripts/test_gpio.py

config.yaml 의 gpio 핀 번호로 LED(녹/황/적)와 부저를 순차 점등/소리 테스트한다.
gpiozero import는 main 내부 — PC에서 import만 해도 깨지지 않게.
"""
from __future__ import annotations


def main() -> None:
    import time

    import yaml
    from gpiozero import LED, Buzzer  # RPi에서만 동작

    with open("config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    pins = cfg["gpio"]
    print("GPIO 핀 설정:", pins)

    # 공통 캐소드 모듈 가정(value=1=점등). 색깔별로 1초씩 차례 점등해 각 핀 배선 확인.
    leds = {
        "녹색(ok)": LED(pins["led_green"]),
        "황색(warn)": LED(pins["led_yellow"]),
        "적색(danger)": LED(pins["led_red"]),
    }
    buzzer = Buzzer(pins["buzzer"])

    try:
        for name, led in leds.items():
            print(f"LED 점등: {name}")
            led.on()
            time.sleep(1)
            led.off()

        print("부저: 짧게")
        buzzer.on()
        time.sleep(0.2)
        buzzer.off()
        time.sleep(0.5)

        print("부저: 길게")
        buzzer.on()
        time.sleep(1)
        buzzer.off()

        print("테스트 완료.")
    finally:
        # Ctrl+C·예외에도 모두 끔
        for led in leds.values():
            led.off()
        buzzer.off()


if __name__ == "__main__":
    main()
