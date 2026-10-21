import esper

from src.ecs.components.c_movement_anim import CMovementAnim, MovementAnimState
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.c_animation import CAnimation


def system_movement_anim(world: esper.World):
    components = world.get_components(CVelocity, CAnimation, CMovementAnim)

    for _, (c_v, c_a, c_m) in components:
        if c_v.vel.x != 0:
            c_m.flip_x = c_v.vel.x < 0
        if c_v.vel.y != 0:
            c_m.flip_y = c_v.vel.y < 0

        if c_m.state == MovementAnimState.IDLE:
            _do_idle_state(c_v, c_a, c_m)
        elif c_m.state == MovementAnimState.MOVE:
            _do_move_state(c_v, c_a, c_m)


def _do_idle_state(
    c_v: CVelocity,
    c_a: CAnimation,
    c_m: CMovementAnim
):
    _set_animation(c_a, "IDLE")
    if c_v.vel.magnitude_squared() > 0:
        c_m.state = MovementAnimState.MOVE

def _do_move_state(
    c_v: CVelocity,
    c_a: CAnimation,
    c_m: CMovementAnim
):
    _set_animation(c_a, "MOVE")
    if c_v.vel.magnitude_squared() <= 0:
            c_m.state = MovementAnimState.IDLE

def _set_animation(c_a: CAnimation, name: str):
    num_anim = _anim_index(c_a, name)
    if c_a.curr_anim == num_anim:
        return

    c_a.curr_anim = num_anim
    c_a.curr_anim_time = 0
    c_a.curr_frame = c_a.animations_list[c_a.curr_anim].start

def _anim_index(c_a: CAnimation, name: str) -> int:
    for index, anim in enumerate(c_a.animations_list):
        if anim.name == name:
            return index
    raise ValueError(name)
