from .base import BaseGesture, get_finger_states, tip_near_finger


class ScissorsGesture(BaseGesture):
    name = "scissors"
    label = "Choki"

    @staticmethod
    def detect(landmarks) -> bool:
        f = get_finger_states(landmarks)
        # 人差し指・中指が伸びている
        two_open = f["index"] and f["middle"]
        # 薬指・小指が曲がっている
        two_closed = not f["ring"] and not f["pinky"]
        # 親指の先が薬指の付け根に近い
        thumb_tucked = tip_near_finger(landmarks, 4, 13, threshold=0.10)
        return two_open and two_closed and thumb_tucked
