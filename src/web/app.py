"""Flask 모니터링 대시보드.

현재 단계·EAR·pitch 등 실시간 상태를 화면에 보여준다.
무거운 import(flask)는 팩토리 함수 내부에 둔다.
"""
from __future__ import annotations

import json
from pathlib import Path


def create_app(state: dict, log_path: str, clip_dir: str = "clips"):
    """Flask 앱을 생성해 반환한다.

    Args:
        state: 메인 루프가 갱신하는 공유 상태 dict
            (예: {"stage": "ok", "ear": 0.3, "pitch": 0.0, "ts": ...}).
            run.py와 웹 서버가 같은 객체를 참조해 최신 값을 노출한다.
        log_path: 졸음 이벤트 로그 JSON 파일 경로 (config.event_log.output_path).

    Returns:
        flask.Flask 인스턴스.
    """
    from flask import Flask, jsonify, render_template, send_from_directory

    app = Flask(__name__)
    clip_root = Path(clip_dir).resolve()

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/status")
    def status():
        # 메인 루프가 갱신한 최신 상태를 JSON으로 반환.
        return jsonify(state)

    @app.route("/logs")
    def logs():
        # 졸음 이벤트 로그(JSON 배열)를 반환. 파일이 없거나 비정상이면 빈 목록.
        try:
            with open(log_path, encoding="utf-8") as f:
                return jsonify(json.load(f))
        except (FileNotFoundError, ValueError):
            return jsonify([])

    @app.route("/clips/<path:filename>")
    def clips(filename: str):
        return send_from_directory(clip_root, filename, conditional=True)

    return app
