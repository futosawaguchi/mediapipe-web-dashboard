from abc import ABC, abstractmethod
import numpy as np


def _dist(a, b) -> float:
    """2点間のユークリッド距離"""
    return np.sqrt((a.x - b.x)**2 + (a.y - b.y)**2 + (a.z - b.z)**2)


def get_finger_states(landmarks) -> dict:
    """
    手のランドマークから各指の状態を返す

    判定基準：
    - 人差し指〜小指：指先と手首の距離 > 指の付け根と手首の距離 なら「伸びている」
    - 親指：指先と中指付け根の距離 > 親指付け根と中指付け根の距離 なら「伸びている」

    Returns:
        {
            "thumb":  bool,  # 親指
            "index":  bool,  # 人差し指
            "middle": bool,  # 中指
            "ring":   bool,  # 薬指
            "pinky":  bool,  # 小指
        }
    """
    wrist = landmarks[0]

    # 各指の付け根・先端のランドマークインデックス
    fingers = {
        "index":  {"base": landmarks[5],  "tip": landmarks[8]},
        "middle": {"base": landmarks[9],  "tip": landmarks[12]},
        "ring":   {"base": landmarks[13], "tip": landmarks[16]},
        "pinky":  {"base": landmarks[17], "tip": landmarks[20]},
    }

    result = {}

    # 人差し指〜小指：指先が手首より付け根から遠ければ「伸びている」
    for name, lm in fingers.items():
        tip_to_wrist  = _dist(lm["tip"],  wrist)
        base_to_wrist = _dist(lm["base"], wrist)
        result[name] = tip_to_wrist > base_to_wrist

    # 親指：指先が中指付け根より親指付け根から遠ければ「伸びている」
    middle_base = landmarks[9]
    result["thumb"] = _dist(landmarks[4], middle_base) > _dist(landmarks[2], middle_base)

    return result


def tip_near_finger(landmarks, tip_idx: int, target_base_idx: int, threshold: float = 0.08) -> bool:
    """
    指先が特定の指の付け根に近いかどうかを判定する
    グーの親指判定・チョキの親指判定などに使用

    Args:
        tip_idx:         指先のランドマークインデックス
        target_base_idx: 基準となる指の付け根インデックス
        threshold:       距離のしきい値
    """
    return _dist(landmarks[tip_idx], landmarks[target_base_idx]) < threshold


class BaseGesture(ABC):
    name: str = ""
    label: str = ""

    @staticmethod
    @abstractmethod
    def detect(landmarks) -> bool:
        raise NotImplementedError