from .base import BaseGesture, get_finger_states

class PaperGesture(BaseGesture):
    name = "paper"
    label = "Paa"

    @staticmethod
    def detect(landmarks) -> bool:
        f = get_finger_states(landmarks)
        return f["thumb"] and f["index"] and f["middle"] and f["ring"] and f["pinky"]