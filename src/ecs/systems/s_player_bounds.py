import esper
import pygame

from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_surface import CSurface
from src.ecs.components.tags.c_tag_player import CTagPlayer


def system_player_bounds(world: esper.World, screen: pygame.Surface):
    screen_rect = screen.get_rect()
    components = world.get_components(CTransform, CSurface, CTagPlayer)

    c_t:CTransform
    c_s:CSurface

    for entity, (c_t, c_s, c_p) in components:
        c_t.pos.x = max(screen_rect.left, min(c_t.pos.x, screen_rect.right - c_s.area.w))
        c_t.pos.y = max(screen_rect.top, min(c_t.pos.y, screen_rect.bottom - c_s.area.h))
