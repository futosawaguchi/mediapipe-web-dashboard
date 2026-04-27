import os

# カメラ設定
CAMERA_ID = 0          # カメラデバイスID（複数カメラがある場合は1, 2...に変更）
FRAME_WIDTH = 640      # フレーム幅
FRAME_HEIGHT = 480     # フレーム高さ
FPS = 30               # フレームレート

# MediaPipe - 手の検出設定
MAX_NUM_HANDS = 1                  # 検出する手の最大数
HAND_DETECTION_CONFIDENCE = 0.7   # 検出の信頼度しきい値（0.0〜1.0）
HAND_TRACKING_CONFIDENCE = 0.5    # トラッキングの信頼度しきい値（0.0〜1.0）

# MediaPipe - 顔の向き推定設定
FACE_DETECTION_CONFIDENCE = 0.5   # 検出の信頼度しきい値（0.0〜1.0）
FACE_TRACKING_CONFIDENCE = 0.5    # トラッキングの信頼度しきい値（0.0〜1.0）

# 機能のデフォルトON/OFF
DEFAULT_HAND_LANDMARK_VISIBLE = True       # 手のランドマーク表示
DEFAULT_FACE_ORIENTATION_ENABLED = False   # 顔の向き推定

# Flask / SocketIO設定
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5002
FLASK_DEBUG = True
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-fallback-secret")

HAND_MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
FACE_MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task"

HAND_MODEL_PATH = "hand_landmarker.task"
FACE_MODEL_PATH = "face_landmarker.task"