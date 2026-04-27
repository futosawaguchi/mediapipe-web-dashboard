import os
import urllib.request

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

import config


def download_model():
    """モデルファイルをダウンロードする（初回のみ）"""
    if not os.path.exists(config.FACE_MODEL_PATH):
        print("顔のモデルをダウンロード中...")
        urllib.request.urlretrieve(config.FACE_MODEL_URL, config.FACE_MODEL_PATH)
        print("顔のモデルダウンロード完了")


class FaceDetector:
    def __init__(self):
        download_model()
        self._latest_result = None
        self.enabled = config.DEFAULT_FACE_ORIENTATION_ENABLED

        base_options = python.BaseOptions(
            model_asset_path=config.FACE_MODEL_PATH
        )
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.LIVE_STREAM,
            num_faces=1,
            min_face_detection_confidence=config.FACE_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.FACE_TRACKING_CONFIDENCE,
            output_facial_transformation_matrixes=True,
            result_callback=self._result_callback,
        )
        self._landmarker = vision.FaceLandmarker.create_from_options(options)
        self._timestamp = 0

    def _result_callback(self, result, output_image, timestamp_ms):
        self._latest_result = result

    def process(self, frame: np.ndarray) -> tuple[np.ndarray, dict | None]:
        """
        フレームを処理して顔の向きを推定する

        Args:
            frame: OpenCVのBGRフレーム

        Returns:
            (描画済みフレーム, 顔の向き dict or None)
            顔の向き: {"yaw": float, "pitch": float, "roll": float}
        """
        if not self.enabled:
            return frame, None

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        self._timestamp += 1
        self._landmarker.detect_async(mp_image, self._timestamp)

        orientation = None

        if self._latest_result and self._latest_result.face_landmarks:
            # 顔の向き推定
            if self._latest_result.facial_transformation_matrixes:
                orientation = self._estimate_orientation(
                    self._latest_result.facial_transformation_matrixes[0]
                )

                # 画面に角度を描画
                self._draw_orientation(frame, orientation)

        return frame, orientation

    def _estimate_orientation(self, matrix) -> dict:
        """変換行列からYaw/Pitch/Rollを計算する"""
        mat = np.array(matrix.data).reshape(4, 4)

        yaw   = float(np.degrees(np.arctan2(mat[2][0], mat[2][2])))
        pitch = float(np.degrees(np.arcsin(-mat[2][1])))
        roll  = float(np.degrees(np.arctan2(mat[0][1], mat[1][1])))

        return {
            "yaw":   round(yaw, 1),
            "pitch": round(pitch, 1),
            "roll":  round(roll, 1),
        }

    def _draw_orientation(self, frame, orientation: dict):
        """顔の向きを画面右上に描画する"""
        yaw   = orientation["yaw"]
        pitch = orientation["pitch"]
        roll  = orientation["roll"]

        h, w, _ = frame.shape
        x = w - 220  # 右上に表示

        texts = [
            f"Yaw:   {yaw:+.1f}",
            f"Pitch: {pitch:+.1f}",
            f"Roll:  {roll:+.1f}",
        ]
        for i, text in enumerate(texts):
            cv2.putText(
                frame, text,
                (x, 30 + i * 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (0, 255, 255), 2,
            )

    def set_enabled(self, enabled: bool):
        """顔の向き推定のON/OFFを切り替える"""
        self.enabled = enabled

    def close(self):
        self._landmarker.close()