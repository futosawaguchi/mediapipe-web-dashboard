from abc import ABC, abstractmethod


class BaseGesture(ABC):
    name: str = ""   # 内部識別名 例: "rock"
    label: str = ""  # 表示名　　 例: "✊ グー"

    @staticmethod
    @abstractmethod
    def detect(fingers: list[bool]) -> bool:
        """
        fingers: [親指, 人差し指, 中指, 薬指, 小指]
        True  = 指が立っている
        False = 指が曲がっている
        """
        raise NotImplementedError