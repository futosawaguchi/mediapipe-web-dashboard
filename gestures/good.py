from .base import BaseGesture, get_finger_states

class GoodGesture(BaseGesture):
    name = "good"
    label = "Good"

    @staticmethod
    def detect(landmarks) -> bool:
        f = get_finger_states(landmarks)
        return (f["thumb"] and not f["index"] and not f["middle"]
                and not f["ring"] and not f["pinky"])