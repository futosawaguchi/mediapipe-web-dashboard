# test_face.py - 顔のランドマーク動作確認用スクリプト
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import urllib.request
import os

# モデルファイルのダウンロード
MODEL_PATH = "face_landmarker.task"
if not os.path.exists(MODEL_PATH):
    print("モデルをダウンロード中...")
    url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task"
    urllib.request.urlretrieve(url, MODEL_PATH)
    print("ダウンロード完了")

# 検出結果を保持する変数
latest_result = None

def result_callback(result, output_image, timestamp_ms):
    global latest_result
    latest_result = result

# FaceLandmarker の設定
base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.LIVE_STREAM,
    num_faces=1,
    min_face_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    output_facial_transformation_matrixes=True,  # 顔の向き推定に必要
    result_callback=result_callback,
)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("カメラが開けませんでした")
    exit()

print("カメラ起動成功")
print("顔をカメラに向けてください")
print("終了するには 'q' を押してください")

timestamp = 0

with vision.FaceLandmarker.create_from_options(options) as landmarker:
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

        if latest_result and latest_result.face_landmarks:
            h, w, _ = frame.shape

            # ランドマークを描画（緑の点）
            for face in latest_result.face_landmarks:
                for lm in face:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (cx, cy), 1, (0, 255, 0), -1)

            # 顔の向き推定（変換行列から Yaw/Pitch/Roll を取得）
            if latest_result.facial_transformation_matrixes:
                import numpy as np
                matrix = latest_result.facial_transformation_matrixes[0]
                mat = np.array(matrix.data).reshape(4, 4)

                # 回転行列からオイラー角を計算
                pitch = np.degrees(np.arcsin(-mat[2][1]))
                yaw   = np.degrees(np.arctan2(mat[2][0], mat[2][2]))
                roll  = np.degrees(np.arctan2(mat[0][1], mat[1][1]))

                print(f"Yaw: {yaw:+.1f}°  Pitch: {pitch:+.1f}°  Roll: {roll:+.1f}°")

                # 画面にも表示
                cv2.putText(frame, f"Yaw:   {yaw:+.1f}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.putText(frame, f"Pitch: {pitch:+.1f}", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.putText(frame, f"Roll:  {roll:+.1f}", (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        cv2.imshow("Face Landmark Test", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()
print("終了しました")