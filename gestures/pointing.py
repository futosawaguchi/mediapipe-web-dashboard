from .base import BaseGesture


class PointingGesture(BaseGesture):
    name = "pointing"
    label = "☝️ ポインティング"

    @staticmethod
    def detect(fingers: list[bool]) -> bool:
        # 人差し指だけ立っていて、他は曲がっている
        return (
            not fingers[0]
            and fingers[1]
            and not fingers[2]
            and not fingers[3]
            and not fingers[4]
        )