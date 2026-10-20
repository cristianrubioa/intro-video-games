import esper

from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.components.tags.c_tag_enemy import CTagEnemy


def system_collision_bullet_enemy(world: esper.World):
    bullets = list(world.get_components(CSurface, CTransform, CTagBullet))
    enemies = list(world.get_components(CSurface, CTransform, CTagEnemy))

    for bullet_entity, (c_s, c_t, _) in bullets:
        bullet_rect = CSurface.get_area_relative(c_s.area, c_t.pos)

        for enemy_entity, (c_b_s, c_b_t, _) in enemies:
            enemy_rect = CSurface.get_area_relative(c_b_s.area, c_b_t.pos)
            if bullet_rect.colliderect(enemy_rect):
                world.delete_entity(bullet_entity)
                world.delete_entity(enemy_entity)
                break
