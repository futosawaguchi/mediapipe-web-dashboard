from .base import BaseGesture


class GoodGesture(BaseGesture):
    name = "good"
    label = "👍 グッド"

    @staticmethod
    def detect(fingers: list[bool]) -> bool:
        # 親指だけ立っていて、他は曲がっている
        return (
            fingers[0]
            and not fingers[1]
            and not fingers[2]
            and not fingers[3]
            and not fingers[4]
        )