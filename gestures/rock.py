from .base import BaseGesture, get_finger_states, tip_near_finger


class RockGesture(BaseGesture):
    name = "rock"
    label = "Guu"

    @staticmethod
    def detect(landmarks) -> bool:
        f = get_finger_states(landmarks)
        # 人差し指〜小指が全て曲がっている
        four_closed = not f["index"] and not f["middle"] and not f["ring"] and not f["pinky"]
        # 親指の先が中指の付け根に近い
        thumb_tucked = tip_near_finger(landmarks, 4, 9, threshold=0.10)
        return four_closed and thumb_tucked