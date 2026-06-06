"""단계별 경고 출력.

PC(Windows)  : ConsoleAlert  - 콘솔에 글자로 표시
RPi(Linux)   : GpioAlert     - LED + 부저 (gpiozero)
둘 다 set_stage(stage), close() 를 가진다.
"""
from __future__ import annotations


class ConsoleAlert:
    _MSG = {"ok": "정상", "warn": "[주의] 졸음 의심", "danger": "[위험] 졸음 감지!!"}

    def __init__(self):
        self._last = None

    def set_stage(self, stage: str) -> None:
        # 매 프레임 호출되므로, 단계가 바뀔 때만 출력
        if stage != self._last:
            print(f"[ALERT] {self._MSG.get(stage, stage)}")
            self._last = stage

    def close(self) -> None:
        pass


class GpioAlert:
    """라즈베리파이에서만 사용 (gpiozero 필요)."""

    def __init__(self, gpio_cfg: dict):
        from gpiozero import LED, Buzzer  # RPi에서만 import
        self.leds = {
            "ok": LED(gpio_cfg["led_green"]),
            "warn": LED(gpio_cfg["led_yellow"]),
            "danger": LED(gpio_cfg["led_red"]),
        }
        self.buzzer = Buzzer(gpio_cfg["buzzer"])

    def set_stage(self, stage: str) -> None:
        for s, led in self.leds.items():
            led.value = 1 if s == stage else 0
        self.buzzer.value = 1 if stage == "danger" else 0

    def close(self) -> None:
        for led in self.leds.values():
            led.off()
        self.buzzer.off()