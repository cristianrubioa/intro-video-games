import esper
import pygame

from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_surface import CSurface
from src.ecs.components.tags.c_tag_bullet import CTagBullet


def system_bullet_bounds(world: esper.World, screen: pygame.Surface):
    screen_rect = screen.get_rect()
    components = world.get_components(CTransform, CSurface, CTagBullet)

    c_t:CTransform
    c_s:CSurface

    for entity, (c_t, c_s, c_b) in components:
        cuad_rect = CSurface.get_area_relative(c_s.area, c_t.pos)

        if (
            cuad_rect.left < 0
            or cuad_rect.right > screen_rect.width
            or cuad_rect.top < 0
            or cuad_rect.bottom > screen_rect.height
        ):
            world.delete_entity(entity)
