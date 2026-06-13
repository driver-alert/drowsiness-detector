"""마이크 입력 진단.

사용:
    python scripts/test_mic.py

1) 인식 가능한 마이크 목록과 기본 장치를 출력한다.
2) 기본 마이크로 약 5초간 녹음하며 음량(RMS)을 0.5초 단위로 출력한다.
   - 말할 때 값이 크게 오르면 마이크가 소리를 잡는 것(정상).
   - 거의 0에 머무르면 장치 선택/음소거 문제 → 아래 device_index로 다른 장치 지정.
3) 녹음본으로 Google STT 인식을 1회 시도한다.

특정 장치로 테스트하려면 환경변수로 인덱스를 지정:
    setx 같은 거 말고, 임시로:  $env:MIC_INDEX=2; python scripts/test_mic.py   (PowerShell)
"""
from __future__ import annotations

import audioop
import os
import time

import speech_recognition as sr


def main() -> None:
    print("=== 마이크 목록 ===")
    for i, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"  [{i}] {name}")

    idx_env = os.environ.get("MIC_INDEX")
    device_index = int(idx_env) if idx_env else None
    mic = sr.Microphone(device_index=device_index)
    print(f"\n사용 device_index: {mic.device_index} (None=기본 장치)")

    r = sr.Recognizer()
    r.energy_threshold = 300
    r.dynamic_energy_threshold = True

    print("\n약 5초간 또렷하게 답을 말하세요 (예: '백' 또는 '오십')...")
    peak = 0
    with mic as source:
        end = time.time() + 5
        next_print = 0.0
        while time.time() < end:
            buf = source.stream.read(source.CHUNK)
            rms = audioop.rms(buf, source.SAMPLE_WIDTH)
            peak = max(peak, rms)
            now = time.time()
            if now >= next_print:
                print(f"  RMS={rms}")
                next_print = now + 0.5
    verdict = "마이크 정상(소리 잡힘)" if peak > 500 else "소리 거의 없음 → 장치/음소거 의심"
    print(f"최대 RMS={peak} → {verdict}")

    print("\n=== STT 인식 시도 (두 음절 이상으로 말하세요. 예: '구십구') ===")
    with mic as source:
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
        except sr.WaitTimeoutError:
            print("→ 청취 타임아웃: 말소리 시작을 감지 못함")
            return

    # 캡처된 구간을 저장/출력해 '무엇이 잡혔는지' 확인 가능하게 한다
    wav = audio.get_wav_data()
    dur = len(audio.frame_data) / (audio.sample_rate * audio.sample_width)
    os.makedirs("logs", exist_ok=True)
    with open("logs/last_stt.wav", "wb") as f:
        f.write(wav)
    print(f"캡처 길이: {dur:.2f}s (저장: logs/last_stt.wav — 재생해서 본인 목소리인지 확인)")

    try:
        resp = r.recognize_google(audio, language="ko-KR", show_all=True)
        print("Google 응답 원문:", resp if resp else "(빈 응답 = 알아듣지 못함)")
    except sr.RequestError as e:
        print("→ 요청 오류(네트워크):", e)


if __name__ == "__main__":
    main()
