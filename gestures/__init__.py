from .rock import RockGesture
from .scissors import ScissorsGesture
from .paper import PaperGesture
from .pointing import PointingGesture
from .good import GoodGesture

# ジェスチャーの判定順序（上から順に評価される）
GESTURE_LIST = [
    RockGesture,
    ScissorsGesture,
    PaperGesture,
    PointingGesture,
    GoodGesture,
]