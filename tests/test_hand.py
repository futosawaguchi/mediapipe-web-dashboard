# test_hand.py - 手のランドマーク動作確認用スクリプト
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import urllib.request
import os

# モデルファイルのダウンロード
MODEL_PATH = "hand_landmarker.task"
if not os.path.exists(MODEL_PATH):
    print("モデルをダウンロード中...")
    url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
    urllib.request.urlretrieve(url, MODEL_PATH)
    print("ダウンロード完了")

# 検出結果を保持する変数
latest_result = None

def result_callback(result, output_image, timestamp_ms):
    global latest_result
    latest_result = result

# HandLandmarker の設定
base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.LIVE_STREAM,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_tracking_confidence=0.5,
    result_callback=result_callback,
)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("カメラが開けませんでした")
    exit()

print("カメラ起動成功")
print("手をカメラに向けてください")
print("終了するには 'q' を押してください")

timestamp = 0

with vision.HandLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("フレームの取得に失敗しました")
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        timestamp += 1
        landmarker.detect_async(mp_image, timestamp)

        # ランドマークを描画
        if latest_result and latest_result.hand_landmarks:
            for hand in latest_result.hand_landmarks:
                h, w, _ = frame.shape
                for lm in hand:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

                # 手首座標をターミナルに表示
                wrist = hand[0]
                print(f"手首: x={wrist.x:.3f}, y={wrist.y:.3f}, z={wrist.z:.3f}")

        cv2.imshow("Hand Landmark Test", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()
print("終了しました")