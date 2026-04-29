import threading

import cv2

import config
from detectors import FaceDetector, HandDetector


class Camera:
    def __init__(self):
        self.cap = cv2.VideoCapture(config.CAMERA_ID)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, config.FPS)

        if not self.cap.isOpened():
            raise RuntimeError("カメラが開けませんでした")

        self.hand_detector = HandDetector()
        self.face_detector = FaceDetector()

        self._lock = threading.Lock()
        self._latest_frame = None
        self._latest_gesture = None
        self._latest_orientation = None
        self._running = False
        self._thread = None

    def start(self):
        """カメラのキャプチャスレッドを開始する"""
        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def _capture_loop(self):
        """フレームを取得し続けるループ（別スレッドで動作）"""
        while self._running:
            ret, frame = self.cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)

            # 手のランドマーク・ジェスチャー判定
            frame, gesture, direction = self.hand_detector.process(frame)

            # 顔の向き推定
            frame, orientation = self.face_detector.process(frame)

            with self._lock:
                self._latest_frame = frame
                self._latest_gesture = gesture
                self._latest_orientation = orientation
                self._latest_direction   = direction

    def get_frame(self) -> bytes | None:
        """
        最新フレームをJPEGのbytesで返す
        Flask側でMJPEGストリームとして配信するために使用する
        """
        with self._lock:
            frame = self._latest_frame

        if frame is None:
            return None

        _, buffer = cv2.imencode(".jpg", frame)
        return buffer.tobytes()

    def get_status(self) -> dict:
        """最新のジェスチャーと顔の向きをまとめて返す"""
        with self._lock:
            return {
                "gesture": self._latest_gesture,
                "orientation": self._latest_orientation,
                "direction":        self._latest_direction,
                "landmark_visible": self.hand_detector.landmark_visible,
                "face_enabled": self.face_detector.enabled,
            }

    def set_landmark_visible(self, visible: bool):
        """手のランドマーク表示のON/OFFを切り替える"""
        self.hand_detector.set_landmark_visible(visible)

    def set_face_enabled(self, enabled: bool):
        """顔の向き推定のON/OFFを切り替える"""
        self.face_detector.set_enabled(enabled)

    def stop(self):
        """カメラとDetectorのリソースを解放する"""
        self._running = False
        if self._thread:
            self._thread.join()
        self.cap.release()
        self.hand_detector.close()
        self.face_detector.close()