
SPECIAL_POP_DURATION = 0.15
SPECIAL_SHAKE_DURATION = 0.12


class CSpecialAttack:
    def __init__(self, cooldown_total: float) -> None:
        self.cooldown_total = cooldown_total
        self.cooldown_remaining = 0.0
        self.pop_timer = 0.0
        self.shake_timer = 0.0
