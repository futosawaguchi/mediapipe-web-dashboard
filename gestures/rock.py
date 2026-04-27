from .base import BaseGesture


class RockGesture(BaseGesture):
    name = "rock"
    label = "✊ グー"

    @staticmethod
    def detect(fingers: list[bool]) -> bool:
        # 全ての指が曲がっている
        return not any(fingers)