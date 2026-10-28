import esper
import pygame

from src.ecs.components.c_hunter import CHunter
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.engine.service_locator import ServiceLocator


def system_hunter_state(world: esper.World, player_entity: int):
    player_t = world.component_for_entity(player_entity, CTransform)
    components = world.get_components(CHunter, CTransform, CVelocity)

    c_h: CHunter
    c_t: CTransform
    c_v: CVelocity

    for _, (c_h, c_t, c_v) in components:
        if c_t.pos.distance_to(c_h.origin) > c_h.distance_start_return:
            _move_towards(c_v, c_t.pos, c_h.origin, c_h.velocity_return)
            c_h.is_chasing = False
        elif c_t.pos.distance_to(player_t.pos) <= c_h.distance_start_chase:
            if not c_h.is_chasing:
                ServiceLocator.sounds_service.play(c_h.sound_chase)
            _move_towards(c_v, c_t.pos, player_t.pos, c_h.velocity_chase)
            c_h.is_chasing = True
        else:
            c_v.vel.x = 0
            c_v.vel.y = 0
            c_h.is_chasing = False


def _move_towards(
    c_v: CVelocity,
    from_pos: pygame.Vector2,
    to_pos: pygame.Vector2,
    speed: float,
):
    direction = to_pos - from_pos
    if direction.length_squared() > 0:
        c_v.vel = direction.normalize() * speed
    else:
        c_v.vel.x = 0
        c_v.vel.y = 0
