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
        cuad_rect = c_s.surf.get_rect(topleft=c_t.pos)
        cuad_rect.clamp_ip(screen_rect)
        c_t.pos.x = cuad_rect.x
        c_t.pos.y = cuad_rect.y
