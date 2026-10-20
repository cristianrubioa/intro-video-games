import esper
import pygame

from src.create.prefab_creator import create_explosion
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_enemy import CTagEnemy

def system_collisions_player_enemy(
    world: esper.World,
    player_entity: int,
    level_cfg: dict,
    explosion_data: dict,
):
    components = world.get_components(CSurface, CTransform, CTagEnemy)
    p1_t = world.component_for_entity(player_entity, CTransform)
    p1_s = world.component_for_entity(player_entity, CSurface)
    p1_rect = CSurface.get_area_relative(p1_s.area, p1_t.pos)

    for enemy_entity, (c_s, c_t, _) in components:
        ene_rect = CSurface.get_area_relative(c_s.area, c_t.pos)
        if ene_rect.colliderect(p1_rect):
            create_explosion(world, explosion_data, pygame.Vector2(ene_rect.center))
            world.delete_entity(enemy_entity)
            p1_t.pos.x = level_cfg["player_spawn"]["position"]["x"] - p1_s.surf.get_width() / 2
            p1_t.pos.y = level_cfg["player_spawn"]["position"]["y"] - p1_s.surf.get_height() / 2