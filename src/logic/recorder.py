"""danger 단계 이벤트 영상 클립 저장.

run.py 사용:
    recorder.feed(frame)                                 # 매 프레임
    clip = recorder.save() if stage == "danger" else None

동작: danger가 시작되면 직전 pre_seconds 영상부터 저장을 시작하고,
danger가 끝난 뒤 post_seconds 만큼 더 기록한 다음 파일을 닫는다.
"""
from __future__ import annotations

import os
import time
from collections import deque

import cv2


class ClipRecorder:
    def __init__(self, cfg: dict):
        self.output_dir = cfg.get("output_dir", "clips")
        self.pre_seconds = float(cfg.get("pre_seconds", 3))
        self.post_seconds = float(cfg.get("post_seconds", 3))
        self.fps = int(cfg.get("fps", 30))  # 설정 파일의 FPS 사용

        os.makedirs(self.output_dir, exist_ok=True)
        self._pre_buffer = deque(maxlen=int(self.pre_seconds * self.fps))
        self._writer = None
        self._path = None
        self._post_left = 0

    def feed(self, frame) -> None:
        self._pre_buffer.append(frame)
        if self._writer is not None:
            self._writer.write(frame)
            if self._post_left > 0:
                self._post_left -= 1
                if self._post_left == 0:
                    self._finish()

    def save(self):
        if self._writer is None and self._pre_buffer:
            self._start(self._pre_buffer[-1])
            for f in self._pre_buffer:      # 직전 몇 초(pre-roll) 먼저 기록
                self._writer.write(f)
            return self._path
        else:
            self._post_left = int(self.post_seconds * self.fps)  # 녹화 연장
            return None

    def _start(self, sample) -> None:
        h, w = sample.shape[:2]
        self._path = os.path.join(self.output_dir, time.strftime("danger_%Y%m%d_%H%M%S.mp4"))
        # 웹 브라우저 재생 호환성을 위해 avc1(H.264) 사용 시도
        fourcc = cv2.VideoWriter_fourcc(*"avc1")
        self._writer = cv2.VideoWriter(self._path, fourcc, self.fps, (w, h))

        if not self._writer.isOpened():
            # avc1 실패 시 mp4v로 폴백 (일부 브라우저에서 재생이 제한될 수 있음)
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            self._writer = cv2.VideoWriter(self._path, fourcc, self.fps, (w, h))

        self._post_left = int(self.post_seconds * self.fps)

    def _finish(self) -> None:
        if self._writer is not None:
            self._writer.release()
            self._writer = None
            self._path = None

    def close(self) -> None:
        self._finish()