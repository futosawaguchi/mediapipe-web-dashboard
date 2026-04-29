from .base import BaseGesture, get_finger_states, thumb_near

class RockGesture(BaseGesture):
    name = "rock"
    label = "Guu"

    @staticmethod
    def detect(landmarks) -> bool:
        f = get_finger_states(landmarks)
        # 人差し指〜小指が全て曲がっている
        four_closed = not f["index"] and not f["middle"] and not f["ring"] and not f["pinky"]
        # 親指が中指付け根(9)に近い
        thumb_tucked = thumb_near(landmarks, target_idx=9, threshold=0.5)
        return four_closed and thumb_tucked