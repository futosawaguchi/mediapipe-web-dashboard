from .base import BaseGesture, get_finger_states, thumb_near

class ScissorsGesture(BaseGesture):
    name = "scissors"
    label = "Choki"

    @staticmethod
    def detect(landmarks) -> bool:
        f = get_finger_states(landmarks)
        two_open   = f["index"] and f["middle"]
        two_closed = not f["ring"] and not f["pinky"]
        thumb_tucked = thumb_near(landmarks, target_idx=13, threshold=0.6)
        return two_open and two_closed and thumb_tucked