import math
import random

import esper
import pygame

from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.ecs.components.tags.c_tag_player import CTagPlayer
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.components.tags.c_tag_explosion import CTagExplosion
from src.ecs.components.c_input_command import CInputCommand
from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_movement_anim import CMovementAnim
from src.ecs.components.c_hunter import CHunter

from src.engine.service_locator import ServiceLocator

def create_sprite(
    ecs_world: esper.World,
    vel: pygame.Vector2,
    position: dict,
    surface: pygame.Surface
) -> int:
    sprite_entity = ecs_world.create_entity()
    ecs_world.add_component(sprite_entity, CTransform(pos=pygame.Vector2(position["x"], position["y"])))
    ecs_world.add_component(sprite_entity, CVelocity(vel))
    ecs_world.add_component(sprite_entity, CSurface.from_surface(surface=surface))
    return sprite_entity

def create_enemy(
    ecs_world: esper.World,
    enemy_data: dict,
    position: dict,
):
    if "velocity_chase" in enemy_data:
        create_enemy_hunter(ecs_world, enemy_data, position)
    else:
        create_enemy_square(ecs_world, enemy_data, position)

def create_enemy_square(
    ecs_world: esper.World,
    enemy_data: dict,
    position: dict,
):
    enemy_surface = ServiceLocator.images_service.get(enemy_data["image"])
    speed = random.uniform(
        enemy_data["velocity_min"],
        enemy_data["velocity_max"],
    )
    angle = random.uniform(0, 2 * math.pi)
    velocity = pygame.Vector2(1, 0).rotate_rad(angle) * speed
    enemy_entity = create_sprite(ecs_world, velocity, position, enemy_surface)
    ServiceLocator.sounds_service.play(enemy_data["sound"])
    ecs_world.add_component(enemy_entity, CTagEnemy())

def create_enemy_hunter(
    ecs_world: esper.World,
    enemy_data: dict,
    position: dict,
):
    enemy_surface = ServiceLocator.images_service.get(enemy_data["image"])
    velocity = pygame.Vector2(0, 0)
    enemy_entity = create_sprite(ecs_world, velocity, position, enemy_surface)
    ecs_world.add_component(enemy_entity, CTagEnemy())
    ecs_world.add_component(
        enemy_entity,
        CHunter(
            origin=pygame.Vector2(position["x"], position["y"]),
            distance_start_chase=enemy_data["distance_start_chase"],
            distance_start_return=enemy_data["distance_start_return"],
            velocity_chase=enemy_data["velocity_chase"],
            velocity_return=enemy_data["velocity_return"],
            sound_chase=enemy_data["sound_chase"],
        ),
    )
    if "animations" in enemy_data:
        ecs_world.add_component(enemy_entity, CAnimation(enemy_data["animations"]))
        ecs_world.add_component(enemy_entity, CMovementAnim())

def create_player_square(
    ecs_world: esper.World,
    player_info: dict,
    player_1v1_info: dict,
) -> int:
    player_surface = ServiceLocator.images_service.get(player_info["image"])
    size = player_surface.get_size()
    frame_size = pygame.Vector2(size[0] / player_info["animations"]["number_frames"], size[1])
    velocity = pygame.Vector2(0,0)
    position_x = player_1v1_info["position"]["x"] - frame_size.x / 2
    position_y = player_1v1_info["position"]["y"] - frame_size.y / 2
    position = {"x": position_x, "y": position_y}
    player_entity = create_sprite(ecs_world, velocity, position, player_surface)
    ecs_world.component_for_entity(player_entity, CSurface).size = frame_size
    ecs_world.add_component(player_entity, CTagPlayer())
    ecs_world.add_component(player_entity, CAnimation(player_info["animations"]))
    ecs_world.add_component(player_entity, CMovementAnim())
    return player_entity

def create_bullet(
    ecs_world: esper.World,
    bullet_data: dict,
    spawn_center: pygame.Vector2,
    direction: pygame.Vector2,
) -> int:
    bullet_surface = ServiceLocator.images_service.get(bullet_data["image"])
    velocity = direction.normalize() * bullet_data["velocity"]
    size = pygame.Vector2(bullet_surface.get_width(), bullet_surface.get_height())
    position = {
        "x": spawn_center.x - size.x / 2,
        "y": spawn_center.y - size.y / 2,
    }
    bullet_entity = create_sprite(ecs_world, velocity, position, bullet_surface)
    ecs_world.add_component(bullet_entity, CTagBullet())
    ServiceLocator.sounds_service.play(bullet_data["sound"])
    return bullet_entity

def create_explosion(
    ecs_world: esper.World,
    explosion_data: dict,
    center: pygame.Vector2,
) -> int:
    explosion_surface = ServiceLocator.images_service.get(explosion_data["image"])
    frame_w = explosion_surface.get_width() / explosion_data["animations"]["number_frames"]
    frame_h = explosion_surface.get_height()
    position = {
        "x": center.x - frame_w / 2,
        "y": center.y - frame_h / 2,
    }
    explosion_entity = create_sprite(ecs_world, pygame.Vector2(0, 0), position, explosion_surface)
    c_animation = CAnimation(explosion_data["animations"])
    for anim in c_animation.animations_list:
        anim.loop = False
    ecs_world.add_component(explosion_entity, c_animation)
    ecs_world.add_component(explosion_entity, CTagExplosion())
    ServiceLocator.sounds_service.play(explosion_data["sound"])
    return explosion_entity

def create_text(
    ecs_world: esper.World,
    text: str,
    font: pygame.font.Font,
    color: pygame.Color,
    position: dict,
) -> int:
    text_entity = ecs_world.create_entity()
    ecs_world.add_component(text_entity, CTransform(pos=pygame.Vector2(position["x"], position["y"])))
    ecs_world.add_component(text_entity, CSurface.from_text(text, font, color))
    return text_entity

def create_enemy_spawner(ecs_world: esper.World, level_data: dict):
    events = [{**event, "fired": False} for event in level_data["enemy_spawn_events"]]
    spawner_entity = ecs_world.create_entity()
    ecs_world.add_component(
        spawner_entity,
        CEnemySpawner(events),
    )

def create_input_player(ecs_world: esper.World):
    input_left = ecs_world.create_entity()
    input_right = ecs_world.create_entity()
    input_up = ecs_world.create_entity()
    input_down = ecs_world.create_entity()
    input_fire = ecs_world.create_entity()

    ecs_world.add_component(
        input_left,
        CInputCommand("PLAYER_LEFT", pygame.K_LEFT)
    )
    ecs_world.add_component(
            input_right,
            CInputCommand("PLAYER_RIGHT", pygame.K_RIGHT)
        )
    ecs_world.add_component(
            input_up,
            CInputCommand("PLAYER_UP", pygame.K_UP)
        )
    ecs_world.add_component(
            input_down,
            CInputCommand("PLAYER_DOWN", pygame.K_DOWN)
        )
    ecs_world.add_component(
            input_fire,
            CInputCommand("PLAYER_FIRE", pygame.BUTTON_LEFT)
        )