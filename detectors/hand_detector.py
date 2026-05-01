import os
import urllib.request

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

import config
from gestures import GESTURE_LIST
from gestures.base import get_finger_states


def download_model():
    """モデルファイルをダウンロードする（初回のみ）"""
    if not os.path.exists(config.HAND_MODEL_PATH):
        print("手のモデルをダウンロード中...")
        urllib.request.urlretrieve(config.HAND_MODEL_URL, config.HAND_MODEL_PATH)
        print("手のモデルダウンロード完了")

def calc_pointing_direction(landmarks) -> dict | None:
    """
    人差し指の付け根(5) → 指先(8) のベクトルから
    水平・垂直・奥行き角度を計算する

    Returns:
        {
            "horizontal": float,  # 水平角度（右が正、左が負）
            "vertical":   float,  # 垂直角度（上が正、下が負）
            "depth":      float,  # 奥行き角度（カメラ方向が正）
            "dx": float,          # 正規化済みベクトル（フロント描画用）
            "dy": float,
        }
    """
    base = landmarks[5]
    tip  = landmarks[8]

    dx = tip.x - base.x
    dy = tip.y - base.y
    dz = tip.z - base.z

    # ベクトルの長さで正規化
    length = np.sqrt(dx**2 + dy**2 + dz**2) + 1e-6
    ndx = dx / length
    ndy = dy / length
    ndz = dz / length

    # 水平角度（右が正・左が負）
    horizontal = float(np.degrees(np.arctan2(ndx, np.sqrt(ndy**2 + ndz**2) + 1e-6)))

    # 垂直角度（上が正・下が負、画像座標系を反転）
    vertical = float(np.degrees(np.arctan2(-ndy, np.sqrt(ndx**2 + ndz**2) + 1e-6)))

    # 奥行き角度（カメラ方向が正）
    depth = float(np.degrees(np.arctan2(-ndz, np.sqrt(ndx**2 + ndy**2) + 1e-6)))

    return {
        "horizontal": round(horizontal, 1),
        "vertical":   round(vertical, 1),
        "depth":      round(depth, 1),
        "dx":         round(ndx, 3),   # フロントの矢印描画用
        "dy":         round(ndy, 3),
    }

class HandDetector:
    CONNECTIONS = [
        (0, 1), (1, 2), (2, 3), (3, 4),
        (0, 5), (5, 6), (6, 7), (7, 8),
        (0, 9), (9, 10), (10, 11), (11, 12),
        (0, 13), (13, 14), (14, 15), (15, 16),
        (0, 17), (17, 18), (18, 19), (19, 20),
        (5, 9), (9, 13), (13, 17),
    ]

    def __init__(self):
        download_model()
        self._latest_result = None
        self.landmark_visible = config.DEFAULT_HAND_LANDMARK_VISIBLE

        base_options = python.BaseOptions(
            model_asset_path=config.HAND_MODEL_PATH
        )
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.LIVE_STREAM,
            num_hands=config.MAX_NUM_HANDS,
            min_hand_detection_confidence=config.HAND_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.HAND_TRACKING_CONFIDENCE,
            result_callback=self._result_callback,
        )
        self._landmarker = vision.HandLandmarker.create_from_options(options)
        self._timestamp = 0

    def _result_callback(self, result, output_image, timestamp_ms):
        self._latest_result = result

    def process(self, frame: np.ndarray) -> tuple[np.ndarray, str | None, dict | None]:
        """
        フレームを処理してランドマーク描画・ジェスチャー判定・指の方向計算を行う

        Returns:
            (描画済みフレーム, ジェスチャーラベル or None, 指の方向 or None)
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        self._timestamp += 1
        self._landmarker.detect_async(mp_image, self._timestamp)

        gesture_label = None
        direction = None

        if self._latest_result and self._latest_result.hand_landmarks:
            h, w, _ = frame.shape
            landmarks = self._latest_result.hand_landmarks[0]

            if self.landmark_visible:
                self._draw_landmarks(frame, landmarks, h, w)

            gesture_label = self._classify(landmarks)
            direction = calc_pointing_direction(landmarks)

        return frame, gesture_label, direction

    def _draw_landmarks(self, frame, landmarks, h, w):
        points = [
            (int(lm.x * w), int(lm.y * h)) for lm in landmarks
        ]
        for start, end in self.CONNECTIONS:
            cv2.line(frame, points[start], points[end], (255, 255, 255), 2)
        for cx, cy in points:
            cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

    def _classify(self, landmarks) -> str | None:
        for gesture in GESTURE_LIST:
            if gesture.detect(landmarks):
                return gesture.label
        return None

    def set_landmark_visible(self, visible: bool):
        self.landmark_visible = visible

    def close(self):
        self._landmarker.close()