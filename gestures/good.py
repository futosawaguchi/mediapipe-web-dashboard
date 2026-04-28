from .base import BaseGesture, get_finger_states


class GoodGesture(BaseGesture):
    name = "good"
    label = "Good"

    @staticmethod
    def detect(landmarks) -> bool:
        f = get_finger_states(landmarks)
        # 親指だけ伸びていて他は全て曲がっている
        return f["thumb"] and not f["index"] and not f["middle"] and not f["ring"] and not f["pinky"]