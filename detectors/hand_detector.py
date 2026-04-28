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


class HandDetector:
    # ランドマークの接続定義（骨格ライン描画用）
    CONNECTIONS = [
        (0, 1), (1, 2), (2, 3), (3, 4),         # 親指
        (0, 5), (5, 6), (6, 7), (7, 8),          # 人差し指
        (0, 9), (9, 10), (10, 11), (11, 12),     # 中指
        (0, 13), (13, 14), (14, 15), (15, 16),   # 薬指
        (0, 17), (17, 18), (18, 19), (19, 20),   # 小指
        (5, 9), (9, 13), (13, 17),               # 手のひら横
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

    def process(self, frame: np.ndarray) -> tuple[np.ndarray, str | None]:
        """
        フレームを処理してランドマーク描画とジェスチャー判定を行う

        Args:
            frame: OpenCVのBGRフレーム

        Returns:
            (描画済みフレーム, ジェスチャーラベル or None)
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        self._timestamp += 1
        self._landmarker.detect_async(mp_image, self._timestamp)

        gesture_label = None

        if self._latest_result and self._latest_result.hand_landmarks:
            h, w, _ = frame.shape
            landmarks = self._latest_result.hand_landmarks[0]

            # ランドマーク・骨格の描画（ON/OFFに応じて）
            if self.landmark_visible:
                self._draw_landmarks(frame, landmarks, h, w)

            # ジェスチャー判定
            fingers = get_finger_states(landmarks)
            gesture_label = self._classify(landmarks)

        return frame, gesture_label

    def _draw_landmarks(self, frame, landmarks, h, w):
        """ランドマークと骨格ラインを描画する"""
        points = [
            (int(lm.x * w), int(lm.y * h)) for lm in landmarks
        ]

        # 骨格ライン（白）
        for start, end in self.CONNECTIONS:
            cv2.line(frame, points[start], points[end], (255, 255, 255), 2)

        # 関節点（緑）
        for cx, cy in points:
            cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

    def _classify(self, landmarks) -> str | None:
        """ランドマークからジェスチャーを判定する"""
        for gesture in GESTURE_LIST:
            if gesture.detect(landmarks):
                return gesture.label
        return None

    def set_landmark_visible(self, visible: bool):
        """ランドマーク表示のON/OFFを切り替える"""
        self.landmark_visible = visible

    def close(self):
        self._landmarker.close()