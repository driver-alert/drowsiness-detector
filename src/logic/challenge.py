"""졸음 각성 산수 챌린지.

danger가 짧은 시간에 반복되면(window_seconds 내 danger_count회) TTS로 두 자리 산수
문제를 음성 출제하고, STT(음성)로 답을 받아 정답/응답시간을 logs/challenges.json에 기록한다.

  ArithmeticChallenge : 문제 출제 1세트(최대 max_problems 재출제) 실행 — 블로킹
  ChallengeManager    : danger 타임스탬프를 모아 트리거 판정 후 백그라운드 스레드로 실행/로깅

무거운 import(pyttsx3, speech_recognition)는 PC 미설치 환경에서도 모듈 import가 깨지지
않도록 메서드 내부에서 한다 (alert.py / web/app.py 컨벤션과 동일).
"""
from __future__ import annotations

import json
import random
import re
import sys
import threading
import time
from collections import deque
from datetime import datetime
from pathlib import Path

# 한국어 수사 -> 숫자 (STT가 숫자를 '구십이'처럼 한글로 줄 때 파싱용)
_KO_ONES = {"일": 1, "이": 2, "삼": 3, "사": 4, "오": 5,
            "육": 6, "칠": 7, "팔": 8, "구": 9, "영": 0, "공": 0}
_KO_UNITS = {"십": 10, "백": 100}


def _korean_to_int(text: str):
    """한글 수사 문자열을 정수로 변환 (예: '구십이' -> 92). 수사 없으면 None."""
    total, cur, found = 0, 0, False
    for ch in text:
        if ch in _KO_ONES:
            cur = _KO_ONES[ch]
            found = True
        elif ch in _KO_UNITS:
            total += (cur or 1) * _KO_UNITS[ch]
            cur = 0
            found = True
        elif ch in ("영", "공"):
            found = True
    total += cur
    return total if found else None


class ArithmeticChallenge:
    """두 자리 산수 문제를 음성 출제하고 답을 듣는 한 세트의 챌린지."""

    def __init__(self, cfg: dict):
        self.max_problems = int(cfg.get("max_problems", 3))
        self.answer_timeout = float(cfg.get("answer_timeout", 7))
        self.operand_min = int(cfg.get("operand_min", 10))
        self.operand_max = int(cfg.get("operand_max", 99))
        self.tts_rate = int(cfg.get("tts_rate", 170))
        idx = cfg.get("mic_device_index")
        self.mic_device_index = int(idx) if idx is not None else None

    def _make_problem(self):
        """두 자리 덧셈/뺄셈 1개 생성 -> (발화 텍스트, 정답).

        한 음절로 발음되는 답은 STT 인식률이 떨어지므로 피한다.
        한 자리수(일~구)는 두 자리수 이상을 보장해 배제하고,
        10(십), 100(백)은 재생성으로 배제한다.
        """
        while True:
            if random.random() < 0.5:
                a = random.randint(self.operand_min, self.operand_max)
                b = random.randint(self.operand_min, self.operand_max)
                text, answer = f"{a} 더하기 {b}", a + b
            else:
                big = random.randint(self.operand_min + 10, self.operand_max)
                small = random.randint(self.operand_min, big - 10)
                text, answer = f"{big} 빼기 {small}", big - small
                
            if answer not in (10, 100):
                return text, answer

    # --- TTS ---
    def _speak(self, text: str) -> None:
        if sys.platform == "win32":
            # run()에서 1회 생성한 엔진을 재사용. pyttsx3 2.99는 2번째 runAndWait가
            # 무음으로 끝나는 버그가 있으나, 2.91에서는 재사용해도 정상 동작한다.
            self._engine.say(text)
            self._engine.runAndWait()
        else:
            self._speak_gtts(text)

    def _speak_gtts(self, text: str) -> None:
        """RPi(Linux)용 발화: gTTS로 mp3 생성 후 mpg123로 재생.

        Linux의 pyttsx3(espeak 드라이버)는 한국어 음성이 없어 gTTS(온라인)를 쓴다.
        STT도 Google 온라인이므로 네트워크 의존은 동일하다. (mpg123는 apt로 설치)
        """
        import subprocess
        import tempfile

        from gtts import gTTS

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            path = f.name
        try:
            gTTS(text=text, lang="ko").save(path)
            subprocess.run(["mpg123", "-q", path], check=False)
        finally:
            Path(path).unlink(missing_ok=True)

    # --- STT ---
    def _listen(self, recognizer, mic):
        """마이크로 한 번 듣고 인식 문자열 반환. 실패/무음이면 None."""
        import speech_recognition as sr

        with mic as source:
            try:
                audio = recognizer.listen(
                    source,
                    timeout=self.answer_timeout,
                    phrase_time_limit=self.answer_timeout,
                )
            except sr.WaitTimeoutError:
                print("[CHALLENGE] 청취 실패: 시간 내 음성 입력 없음")
                return None
        try:
            return recognizer.recognize_google(audio, language="ko-KR")
        except sr.UnknownValueError:
            print("[CHALLENGE] 인식 실패: 음성을 알아듣지 못함")
            return None
        except sr.RequestError as e:
            print(f"[CHALLENGE] 인식 실패: STT 서버 요청 오류 ({e})")
            return None

    def _parse_number(self, text):
        """인식 문자열에서 정수를 추출. 실패 시 None."""
        if not text:
            return None
        m = re.search(r"-?\d+", text)
        if m:
            return int(m.group())
        return _korean_to_int(text)  # '구십이' 같은 한글 수사 답 처리

    def run(self) -> dict:
        """문제를 최대 max_problems회 출제/청취하고 결과 dict를 반환한다."""
        import speech_recognition as sr

        if sys.platform == "win32":
            import pyttsx3

            self._engine = pyttsx3.init()  # 챌린지 1세트 동안 엔진 재사용
            self._engine.setProperty("rate", self.tts_rate)

        recognizer = sr.Recognizer()
        # adjust_for_ambient_noise는 조용한 방에서도 임계값을 과도하게 높여
        # 목소리가 문턱을 못 넘는(=WaitTimeoutError) 경우가 잦다. 기본 임계값 +
        # 동적 조정을 사용해 말소리 시작을 안정적으로 감지한다.
        recognizer.energy_threshold = 300
        recognizer.dynamic_energy_threshold = True
        print(f"[CHALLENGE] energy_threshold={recognizer.energy_threshold}")
        mic = sr.Microphone(device_index=self.mic_device_index)

        problems: list[str] = []
        recognized: list = []
        answer = None
        start = None  # 첫 문제 발화 완료 시점

        for _ in range(self.max_problems):
            text, answer = self._make_problem()
            problems.append(text)
            self._speak(text)
            if start is None:
                start = time.monotonic()

            heard = self._listen(recognizer, mic)
            recognized.append(heard)
            guess = self._parse_number(heard)
            print(f"[CHALLENGE] 문제: {text} = {answer} / 들은 답: {heard!r} -> {guess}")

            if guess is not None and guess == answer:
                self._speak("정답입니다.")
                return {
                    "problems": problems,
                    "answer": answer,
                    "correct": True,
                    "problems_issued": len(problems),
                    "response_time_sec": round(time.monotonic() - start, 2),
                    "recognized": recognized,
                }

        # max_problems 모두 실패 -> 정차 안내 경고
        self._speak("정답을 맞히지 못했습니다. 안전한 곳에 정차하세요.")
        return {
            "problems": problems,
            "answer": answer,
            "correct": False,
            "problems_issued": len(problems),
            "response_time_sec": None,
            "recognized": recognized,
        }


class ChallengeManager:
    """danger 반복을 감지해 챌린지를 트리거하고 결과를 로깅한다."""

    def __init__(self, cfg: dict):
        ch = cfg.get("challenge", {}) or {}
        self.enabled = bool(ch.get("enabled", False))
        self.danger_count = int(ch.get("danger_count", 3))
        self.window_seconds = float(ch.get("window_seconds", 60))
        self.log_path = ch.get("log_path", "logs/challenges.json")
        self._cfg = ch

        self._danger_ts: deque = deque()
        self._lock = threading.Lock()
        self._running = False

        if self.enabled:
            Path(self.log_path).parent.mkdir(parents=True, exist_ok=True)

    def on_danger(self, ts: float) -> None:
        """danger 진입 시점을 기록하고, 윈도우 내 누적이 임계 이상이면 챌린지를 띄운다."""
        if not self.enabled:
            return
        with self._lock:
            if self._running:  # 진행 중이면 무시 (중복 출제 방지)
                return
            self._danger_ts.append(ts)
            while self._danger_ts and ts - self._danger_ts[0] > self.window_seconds:
                self._danger_ts.popleft()
            if len(self._danger_ts) < self.danger_count:
                return
            self._running = True
            self._danger_ts.clear()  # 트리거 후 재발화 방지

        threading.Thread(target=self._run_once, daemon=True, name="challenge").start()

    def _run_once(self) -> None:
        try:
            result = ArithmeticChallenge(self._cfg).run()
            self._log(result)
        except Exception as e:  # 마이크/네트워크 실패해도 메인 루프는 지속
            print(f"[CHALLENGE] 실행 실패: {e}")
        finally:
            with self._lock:
                self._running = False

    def _log(self, result: dict) -> None:
        entry = {"time": datetime.now().isoformat(timespec="seconds"), **result}
        path = Path(self.log_path)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, list):
                data = []
        except (FileNotFoundError, json.JSONDecodeError):
            data = []
        data.append(entry)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(
            f"[CHALLENGE] 기록: correct={result['correct']} "
            f"response_time={result['response_time_sec']}"
        )
