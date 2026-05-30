"""단계별 경고 출력.

판단 단계("ok"/"warn"/"danger")를 받아 물리적/논리적 경고로 변환한다.

- ConsoleAlert : PC 개발용. LED/부저 대신 콘솔에 출력. GPIO 의존성 없음.
- GpioAlert    : RPi 전용. gpiozero(백엔드 lgpio)로 LED·부저 제어.
                 gpiozero import는 메서드 내부 — PC에서 이 파일을 import해도 안전.

단계 정의:
    ok     — 녹색 LED · 무음
    warn   — 황색 LED · 짧은 부저
    danger — 적색 LED · 연속 부저 (+ 클립 저장은 호출측 책임)
"""
from __future__ import annotations


class Alert:
    """경고 출력 인터페이스. run.py는 이 인터페이스에만 의존한다."""

    def set_stage(self, stage: str) -> None:
        """현재 단계("ok"/"warn"/"danger")에 맞는 경고를 출력한다."""
        raise NotImplementedError

    def close(self) -> None:
        """리소스 정리(LED 소등, 핀 해제 등)."""
        raise NotImplementedError


class ConsoleAlert(Alert):
    """PC 개발용 — 콘솔에 단계를 출력한다 (GPIO 없음)."""

    def set_stage(self, stage: str) -> None:
        # TODO: 단계 전환 시에만 출력하도록 직전 단계 비교(스팸 방지).
        if stage == "danger":
            print("[ALERT] 위험 단계")
        elif stage == "warn":
            print("[ALERT] 주의 단계")
        # ok 단계는 무음/무출력.

    def close(self) -> None:
        pass


class GpioAlert(Alert):
    """RPi 전용 — gpiozero로 LED 3색 + 부저를 제어한다."""

    def __init__(self, cfg: dict):
        """Args:
            cfg: config.yaml 의 gpio 설정 (led_green, led_yellow, led_red, buzzer 핀 번호).
        """
        self.cfg = cfg
        # TODO: from gpiozero import LED, Buzzer  (import는 여기서 — PC import 안전)
        #   핀 번호로 LED/Buzzer 객체 생성해 보관.
        raise NotImplementedError("GpioAlert 초기화 미구현")

    def set_stage(self, stage: str) -> None:
        # TODO: stage에 따라 해당 LED on/나머지 off, 부저 패턴(warn=짧게, danger=연속).
        raise NotImplementedError("GpioAlert.set_stage 미구현")

    def close(self) -> None:
        # TODO: 모든 LED/부저 off, 핀 해제.
        raise NotImplementedError("GpioAlert.close 미구현")
