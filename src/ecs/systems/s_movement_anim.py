import esper

from src.ecs.components.c_movement_anim import CMovementAnim, MovementAnimState
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_hunter import CHunter
from src.engine.service_locator import ServiceLocator


def system_movement_anim(world: esper.World):
    components = world.get_components(CVelocity, CAnimation, CMovementAnim)

    for ent, (c_v, c_a, c_m) in components:
        if c_v.vel.x != 0:
            c_m.flip_x = c_v.vel.x < 0
        if c_v.vel.y != 0:
            c_m.flip_y = c_v.vel.y < 0

        sound_chase = world.component_for_entity(ent, CHunter).sound_chase if world.has_component(ent, CHunter) else None

        if c_m.state == MovementAnimState.IDLE:
            _do_idle_state(c_v, c_a, c_m, sound_chase)
        elif c_m.state == MovementAnimState.MOVE:
            _do_move_state(c_v, c_a, c_m, sound_chase)


def _do_idle_state(
    c_v: CVelocity,
    c_a: CAnimation,
    c_m: CMovementAnim,
    sound_chase: str = None
):
    _set_animation(c_a, "IDLE", sound_chase)
    if c_v.vel.magnitude_squared() > 0:
        c_m.state = MovementAnimState.MOVE

def _do_move_state(
    c_v: CVelocity,
    c_a: CAnimation,
    c_m: CMovementAnim,
    sound_chase: str = None
):
    _set_animation(c_a, "MOVE", sound_chase)
    if c_v.vel.magnitude_squared() <= 0:
            c_m.state = MovementAnimState.IDLE

def _set_animation(c_a: CAnimation, name: str, sound_chase: str = None):
    num_anim = _anim_index(c_a, name)
    if c_a.curr_anim == num_anim:
        return

    if sound_chase:
        ServiceLocator.sounds_service.play(sound_chase)

    c_a.curr_anim = num_anim
    c_a.curr_anim_time = 0
    c_a.curr_frame = c_a.animations_list[c_a.curr_anim].start

def _anim_index(c_a: CAnimation, name: str) -> int:
    for index, anim in enumerate(c_a.animations_list):
        if anim.name == name:
            return index
    raise ValueError(name)
