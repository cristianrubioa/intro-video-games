import esper

from src.ecs.components.c_special_attack import CSpecialAttack
from src.ecs.components.c_special_attack import SPECIAL_POP_DURATION


def system_special_attack_state(world: esper.World, delta_time: float):
    for _, c_sa in world.get_component(CSpecialAttack):
        was_ready = c_sa.cooldown_remaining <= 0
        if c_sa.cooldown_remaining > 0:
            c_sa.cooldown_remaining = max(0.0, c_sa.cooldown_remaining - delta_time)
        is_ready = c_sa.cooldown_remaining <= 0

        if is_ready and not was_ready:
            c_sa.pop_timer = SPECIAL_POP_DURATION
        elif c_sa.pop_timer > 0:
            c_sa.pop_timer = max(0.0, c_sa.pop_timer - delta_time)

        if c_sa.shake_timer > 0:
            c_sa.shake_timer = max(0.0, c_sa.shake_timer - delta_time)
