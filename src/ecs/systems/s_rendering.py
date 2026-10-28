import esper
import pygame

from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_movement_anim import CMovementAnim


def system_rendering(world: esper.World, screen: pygame.Surface, offset: pygame.Vector2 = None):
    if offset is None:
        offset = pygame.Vector2(0, 0)
    components = world.get_components(CTransform, CSurface)

    c_t:CTransform
    c_s:CSurface

    for entity, (c_t, c_s) in components:
        pos = c_t.pos + offset
        c_m = world.try_component(entity, CMovementAnim)
        if c_m and (c_m.flip_x or c_m.flip_y):
            frame = pygame.transform.flip(c_s.surf.subsurface(c_s.area), c_m.flip_x, c_m.flip_y)
            screen.blit(frame, pos)
        else:
            screen.blit(c_s.surf, pos, area=c_s.area)