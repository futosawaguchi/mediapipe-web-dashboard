from .base import BaseGesture


class PaperGesture(BaseGesture):
    name = "paper"
    label = "✋ パー"

    @staticmethod
    def detect(fingers: list[bool]) -> bool:
        # 全ての指が立っている
        return all(fingers)