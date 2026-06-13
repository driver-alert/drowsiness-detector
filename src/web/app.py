"""Flask monitoring dashboard for the drowsiness detector."""
from __future__ import annotations

import json
import time


FALLBACK_JPEG = b"\xff\xd8\xff\xd9"


def _get_frame_bytes(frame_store: dict | None) -> bytes | None:
    if not frame_store:
        return None

    lock = frame_store.get("lock")
    if lock is None:
        return frame_store.get("jpeg")

    with lock:
        return frame_store.get("jpeg")


def _placeholder_frame() -> bytes:
    try:
        import cv2
        import numpy as np

        img = np.full((360, 640, 3), 245, dtype=np.uint8)
        cv2.rectangle(img, (0, 0), (639, 359), (220, 226, 235), 2)
        cv2.putText(img, "Waiting for camera frame", (120, 176), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (80, 90, 105), 2)
        ok, encoded = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if ok:
            return encoded.tobytes()
    except Exception:
        pass
    return FALLBACK_JPEG


def _mjpeg_stream(frame_store: dict | None):
    placeholder = _placeholder_frame()
    while True:
        frame = _get_frame_bytes(frame_store) or placeholder
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n"
            b"Cache-Control: no-cache\r\n\r\n" + frame + b"\r\n"
        )
        time.sleep(0.05)


def create_app(state: dict, log_path: str, frame_store: dict | None = None):
    """Create the Flask dashboard app.

    Args:
        state: Shared status updated by the main loop.
        log_path: Event log JSON path.
        frame_store: Optional shared latest JPEG frame store for /video.
    """
    from flask import Flask, Response, jsonify, render_template

    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/status")
    def status():
        return jsonify(state)

    @app.route("/logs")
    def logs():
        try:
            with open(log_path, encoding="utf-8") as f:
                return jsonify(json.load(f))
        except (FileNotFoundError, ValueError):
            return jsonify([])

    @app.route("/video")
    def video():
        return Response(
            _mjpeg_stream(frame_store),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )

    return app
