from enum import Enum

class CMovementAnim:
    def __init__(self) -> None:
        self.state = MovementAnimState.IDLE
        self.flip_x = False
        self.flip_y = False

class MovementAnimState(Enum):
    IDLE = 0
    MOVE = 1
