# drowsiness-detector

실시간 운전자 졸음 감지 시스템. 웹캠/RPi 카메라로 얼굴을 추적해 EAR(눈 감김)과
머리 자세(고개 숙임)로 졸음을 3단계(`ok`/`warn`/`danger`)로 판단하고, 단계별 경고
(LED·부저)와 위험 구간 영상 클립 저장, 웹 대시보드를 제공한다.

> 현재 상태: **스켈레톤** — 디렉터리 구조·인터페이스·설정만 구성됨. 각 모듈의 알고리즘
> 구현은 진행 예정(스텁은 `NotImplementedError`를 던진다).

## 프로젝트 구조

```
src/
├─ run.py            # 메인 루프 (--source webcam|picamera)
├─ vision/           # landmarks(MediaPipe), ear, head_pose
├─ logic/            # drowsiness(3단계 판단), recorder(클립 저장), event_log(이벤트 로그)
├─ hardware/alert.py # ConsoleAlert(PC) / GpioAlert(RPi)
├─ camera/           # webcam(PC) / picamera(RPi)
└─ web/              # Flask 대시보드
models/              # .task 모델 (git 미포함)
scripts/             # download_model.py, test_gpio.py
config.yaml          # 임계값·핀 번호 (코드 하드코딩 금지)
logs/                # 졸음 이벤트 로그 events.json (런타임 산출물, git 미포함)
```

졸음 단계 전이는 `logs/events.json`(JSON 배열)에 기록되며, Flask 대시보드의 **이벤트 로그**
테이블(`/logs`)에서 확인할 수 있다. 기록 대상 단계는 `config.yaml`의 `event_log.log_stages`로 조정한다.

설계 규칙: 하드웨어 의존 코드는 `hardware/`·`camera/`에만 격리하고, 임계값/핀 번호는
`config.yaml` 한 곳에서만 관리한다. 메인 루프는 실행 환경에 맞는 카메라/경고 객체를 주입받는다.

## PC 개발 환경

이 저장소의 PC에는 Python 3.11이 없을 수 있다. 3.10으로 충분하다(RPi는 3.11 사용).

```powershell
py -3.10 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt        # PC는 GPIO 패키지 불필요

python scripts\download_model.py       # Face Landmarker .task 모델 다운로드
python -m src.run --source webcam       # 실행
```

PC에는 GPIO가 없으므로 경고는 콘솔(`[ALERT] ...`)로 출력된다.

## 라즈베리파이 5 환경

```bash
sudo apt update && sudo apt full-upgrade -y
sudo apt install -y python3-venv python3-dev libgl1 libatlas-base-dev python3-picamera2
rpicam-hello --timeout 2000            # 카메라 확인

python3 -m venv --system-site-packages .venv   # picamera2(시스템 패키지) 사용
source .venv/bin/activate
pip install -r requirements.txt -r requirements-rpi.txt

python scripts/test_gpio.py            # LED/부저 배선 확인
python -m src.run --source picamera     # 실제 카메라 + GPIO 실행
```

### USB 마이크/스피커 (각성 챌린지 음성)

```bash
sudo apt install -y portaudio19-dev flac mpg123   # PyAudio 빌드 / STT flac / gTTS mp3 재생
pip install -r requirements.txt -r requirements-rpi.txt

arecord -l                         # USB 마이크 인식 확인
aplay -l                           # USB 스피커 인식 확인
# 기본 출력을 USB 스피커로: 데스크톱은 작업 표시줄 볼륨 아이콘에서 선택, 헤드리스는 raspi-config

python scripts/test_mic.py         # 마이크 RMS·STT 확인 (다른 장치 시험: MIC_INDEX=n)
python scripts/test_challenge.py   # TTS 출제 → STT 응답 전체 흐름
```

기본 장치가 USB 마이크가 아니면 `test_mic.py` 목록의 인덱스를 `config.yaml`의
`challenge.mic_device_index`에 지정한다. 발화는 Windows에서 pyttsx3, RPi에서 gTTS(온라인)를 쓴다.

## 설정

임계값·핀 번호·카메라/웹 설정은 [`config.yaml`](config.yaml)에서 조정한다.
