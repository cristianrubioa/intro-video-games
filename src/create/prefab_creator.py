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
from src.ecs.components.c_input_command import CInputCommand

def create_square(
    ecs_world: esper.World,
    size: pygame.Vector2,
    col: pygame.Color,
    vel: pygame.Vector2,
    position: dict,
) -> int:
    cuad_entity = ecs_world.create_entity()
    ecs_world.add_component(
        cuad_entity,
        CSurface(size=size, color=col),
    )
    ecs_world.add_component(
        cuad_entity,
        CTransform(pos=pygame.Vector2(position["x"], position["y"])),
    )
    ecs_world.add_component(
        cuad_entity,
        CVelocity(vel=vel),
    )
    return cuad_entity

def create_enemy_square(
    ecs_world: esper.World,
    enemy_data: dict,
    position: dict,
):
    size = pygame.Vector2(
        enemy_data["size"]["x"], 
        enemy_data["size"]["y"],
    )
    color = pygame.Color(
        enemy_data["color"]["r"], 
        enemy_data["color"]["g"], 
        enemy_data["color"]["b"],
    )
    speed = random.uniform(
        enemy_data["velocity_min"], 
        enemy_data["velocity_max"],
    )
    angle = random.uniform(0, 2 * math.pi)
    velocity = pygame.Vector2(1, 0).rotate_rad(angle) * speed
    enemy_entity = create_square(ecs_world, size, color, velocity, position)
    ecs_world.add_component(enemy_entity, CTagEnemy())

def create_player_square(
    ecs_world: esper.World,
    player_info: dict,
    player_1v1_info: dict,
) -> int:
    size = pygame.Vector2(
        player_info["size"]["x"], 
        player_info["size"]["y"],
    )
    color = pygame.Color(
        player_info["color"]["r"], 
        player_info["color"]["g"], 
        player_info["color"]["b"],
    )
    velocity = pygame.Vector2(0,0)
    position_x = player_1v1_info["position"]["x"] - size.x / 2
    position_y = player_1v1_info["position"]["y"] - size.y / 2
    position = {"x": position_x, "y": position_y}
    player_entity = create_square(ecs_world, size, color, velocity, position)
    ecs_world.add_component(player_entity, CTagPlayer())
    return player_entity

def create_bullet(
    ecs_world: esper.World,
    bullet_data: dict,
    spawn_center: pygame.Vector2,
    direction: pygame.Vector2,
) -> int:
    size = pygame.Vector2(
        bullet_data["size"]["x"],
        bullet_data["size"]["y"],
    )
    color = pygame.Color(
        bullet_data["color"]["r"],
        bullet_data["color"]["g"],
        bullet_data["color"]["b"],
    )
    velocity = direction.normalize() * bullet_data["velocity"]
    position = {
        "x": spawn_center.x - size.x / 2,
        "y": spawn_center.y - size.y / 2,
    }
    bullet_entity = create_square(ecs_world, size, color, velocity, position)
    ecs_world.add_component(bullet_entity, CTagBullet())
    return bullet_entity

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