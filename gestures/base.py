from abc import ABC, abstractmethod
import numpy as np


def get_finger_states(landmarks) -> list[bool]:
    """
    手のランドマークから各指の状態を返す
    
    手首→中指付け根のベクトルを基準にして
    各指が伸びているか(True)曲がっているか(False)を判定する
    
    Returns:
        [親指, 人差し指, 中指, 薬指, 小指]
        True = 伸びている / False = 曲がっている
    """
    def to_vec(a, b):
        """ランドマークa → bのベクトル"""
        return np.array([b.x - a.x, b.y - a.y, b.z - a.z])

    # 手の基準方向：手首(0) → 中指付け根(9)
    hand_dir = to_vec(landmarks[0], landmarks[9])

    fingers = []

    # 親指：付け根(2) → 先端(4)
    thumb_vec = to_vec(landmarks[2], landmarks[4])
    fingers.append(np.dot(thumb_vec, hand_dir) > 0)

    # 人差し指：付け根(5) → 先端(8)
    index_vec = to_vec(landmarks[5], landmarks[8])
    fingers.append(np.dot(index_vec, hand_dir) > 0)

    # 中指：付け根(9) → 先端(12)
    middle_vec = to_vec(landmarks[9], landmarks[12])
    fingers.append(np.dot(middle_vec, hand_dir) > 0)

    # 薬指：付け根(13) → 先端(16)
    ring_vec = to_vec(landmarks[13], landmarks[16])
    fingers.append(np.dot(ring_vec, hand_dir) > 0)

    # 小指：付け根(17) → 先端(20)
    pinky_vec = to_vec(landmarks[17], landmarks[20])
    fingers.append(np.dot(pinky_vec, hand_dir) > 0)

    return fingers  # [親指, 人差し指, 中指, 薬指, 小指]


class BaseGesture(ABC):
    name: str = ""   # 内部識別名 例: "rock"
    label: str = ""  # 表示名　　 例: "✊ グー"

    @staticmethod
    @abstractmethod
    def detect(fingers: list[bool]) -> bool:
        """
        fingers: [親指, 人差し指, 中指, 薬指, 小指]
        True  = 指が伸びている
        False = 指が曲がっている
        """
        raise NotImplementedError