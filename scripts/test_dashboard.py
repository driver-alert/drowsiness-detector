"""Run the Flask dashboard with mock data, without a webcam or Raspberry Pi.

Usage:
    python scripts/test_dashboard.py

Then open:
    http://127.0.0.1:5000
"""
from __future__ import annotations

import argparse
import json
import threading
import time
from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.web.app import create_app


MOCK_SEQUENCE = [
    {"stage": "ok", "ear": 0.34, "pitch": 2.5},
    {"stage": "ok", "ear": 0.31, "pitch": 4.2},
    {"stage": "warn", "ear": 0.22, "pitch": 9.8},
    {"stage": "danger", "ear": 0.13, "pitch": 21.4},
    {"stage": "warn", "ear": 0.24, "pitch": 13.1},
]


def update_mock_frame(frame_store: dict, item: dict) -> None:
    import cv2
    import numpy as np

    stage = item["stage"]
    colors = {
        "ok": (91, 134, 22),
        "warn": (8, 121, 183),
        "danger": (43, 51, 201),
    }
    img = np.full((360, 640, 3), (246, 248, 250), dtype=np.uint8)
    cv2.rectangle(img, (0, 0), (639, 359), colors.get(stage, (80, 90, 105)), 10)
    cv2.putText(img, f"MOCK CAMERA - {stage.upper()}", (72, 142), cv2.FONT_HERSHEY_SIMPLEX, 1.15, colors.get(stage, (80, 90, 105)), 3)
    cv2.putText(img, f"EAR {item['ear']:.3f}   PITCH {item['pitch']:.1f}", (126, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (42, 50, 62), 2)
    cv2.putText(img, datetime.now().strftime("%H:%M:%S"), (246, 270), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (105, 115, 130), 2)

    ok, encoded = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 82])
    if not ok:
        return

    with frame_store["lock"]:
        frame_store["jpeg"] = encoded.tobytes()
        frame_store["updated"] = time.time()


def update_mock_state(state: dict, log_path: Path, interval: float, frame_store: dict) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    events = []
    prev_stage = None

    while True:
        for item in MOCK_SEQUENCE:
            now = time.time()
            state.update(
                stage=item["stage"],
                ear=item["ear"],
                pitch=item["pitch"],
                ts=now,
            )
            update_mock_frame(frame_store, item)

            if item["stage"] != prev_stage:
                events.append(
                    {
                        "ts": now,
                        "time": datetime.now().isoformat(timespec="seconds"),
                        "stage": item["stage"],
                        "ear": item["ear"],
                        "pitch": item["pitch"],
                        "clip": "clips/mock_danger.mp4" if item["stage"] == "danger" else None,
                    }
                )
                events = events[-30:]
                log_path.write_text(
                    json.dumps(events, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                prev_stage = item["stage"]

            time.sleep(interval)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run dashboard with mock drowsiness data.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--log-path", default="logs/mock_events.json")
    args = parser.parse_args()

    state = {"stage": "ok", "ear": None, "pitch": None, "ts": None}
    frame_store = {"jpeg": None, "updated": None, "lock": threading.Lock()}
    log_path = Path(args.log_path)

    worker = threading.Thread(
        target=update_mock_state,
        args=(state, log_path, args.interval, frame_store),
        daemon=True,
    )
    worker.start()

    app = create_app(state, str(log_path), frame_store)
    print(f"Mock dashboard running: http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
