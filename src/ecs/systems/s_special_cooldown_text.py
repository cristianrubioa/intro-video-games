import esper
import pygame

from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform


def system_special_cooldown_text(
    world: esper.World,
    text_entity: int,
    font: pygame.font.Font,
    cooldown_remaining: float,
    cooldown_cfg: dict,
    anchor: dict,
    pop_scale: float = 1.0,
):
    if cooldown_remaining <= 0:
        text = cooldown_cfg["ready_text"]
        color = cooldown_cfg["ready_color"]
    else:
        text = f"{cooldown_remaining:.1f}"
        color = cooldown_cfg["cooldown_color"]

    surface = font.render(text, True, color)
    if pop_scale != 1.0:
        surface = pygame.transform.scale(
            surface,
            (round(surface.get_width() * pop_scale), round(surface.get_height() * pop_scale)),
        )

    c_transform = world.component_for_entity(text_entity, CTransform)
    c_transform.pos = pygame.Vector2(
        anchor["x"] - surface.get_width() / 2,
        anchor["y"] - surface.get_height() / 2,
    )

    c_surface = world.component_for_entity(text_entity, CSurface)
    c_surface.surf = surface
    c_surface.size = pygame.Vector2(surface.get_size())
    c_surface.area = surface.get_rect()
