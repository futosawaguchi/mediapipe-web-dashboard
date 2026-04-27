import os

from dotenv import load_dotenv
from flask import Flask, Response, render_template
from flask_socketio import SocketIO

import config
from camera import Camera

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-fallback-secret")
socketio = SocketIO(app, cors_allowed_origins="*")

camera = Camera()


# ルーティング
@app.route("/")
def index():
    """メインページ"""
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    """MJPEGストリームを配信するエンドポイント"""
    return Response(
        _generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


def _generate_frames():
    """フレームをMJPEG形式で生成するジェネレーター"""
    while True:
        frame = camera.get_frame()
        if frame is None:
            continue
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        )


# SocketIOイベント
@socketio.on("connect")
def on_connect():
    """クライアント接続時に現在の状態を送信する"""
    status = camera.get_status()
    socketio.emit("status", status)


@socketio.on("toggle_landmark")
def on_toggle_landmark(data):
    """
    手のランドマーク表示のON/OFFを切り替える
    フロントから {"visible": true/false} を受け取る
    """
    visible = data.get("visible", True)
    camera.set_landmark_visible(visible)
    socketio.emit("status", camera.get_status())


@socketio.on("toggle_face")
def on_toggle_face(data):
    """
    顔の向き推定のON/OFFを切り替える
    フロントから {"enabled": true/false} を受け取る
    """
    enabled = data.get("enabled", False)
    camera.set_face_enabled(enabled)
    socketio.emit("status", camera.get_status())


# ステータス送信ループ
def _emit_status_loop():
    """ジェスチャー・顔の向きを定期的にフロントに送信する"""
    while True:
        socketio.sleep(0.1)  # 100ms間隔
        status = camera.get_status()
        socketio.emit("status", status)


# エントリーポイント
if __name__ == "__main__":
    camera.start()
    socketio.start_background_task(_emit_status_loop)
    try:
        socketio.run(
            app,
            host=config.FLASK_HOST,
            port=config.FLASK_PORT,
            debug=config.FLASK_DEBUG,
            use_reloader=False,  # カメラの二重起動を防ぐ
        )
    finally:
        camera.stop()