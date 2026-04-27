from .base import BaseGesture


class ScissorsGesture(BaseGesture):
    name = "scissors"
    label = "✌️ チョキ"

    @staticmethod
    def detect(fingers: list[bool]) -> bool:
        # 人差し指・中指が立っていて、親指・薬指・小指が曲がっている
        return (
            not fingers[0]
            and fingers[1]
            and fingers[2]
            and not fingers[3]
            and not fingers[4]
        )