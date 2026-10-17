import math
import random

import esper
import pygame

from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity

def create_square(
    ecs_world: esper.World,
    size: pygame.Vector2,
    col: pygame.Color,
    vel: pygame.Vector2,
    position: dict,
):
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

def create_enemy_square(
    ecs_world: esper.World,
    enemy_data: dict,
    position: dict,
):
    size = pygame.Vector2(enemy_data["size"]["x"], enemy_data["size"]["y"])
    col = pygame.Color(enemy_data["color"]["r"], enemy_data["color"]["g"], enemy_data["color"]["b"])
    speed = random.uniform(enemy_data["velocity_min"], enemy_data["velocity_max"])
    angle = random.uniform(0, 2 * math.pi)
    vel = pygame.Vector2(1, 0).rotate_rad(angle) * speed
    create_square(ecs_world, size, col, vel, position)

def create_enemy_spawner(ecs_world: esper.World, level_data: dict):
    events = [{**event, "fired": False} for event in level_data["enemy_spawn_events"]]
    spawner_entity = ecs_world.create_entity()
    ecs_world.add_component(
        spawner_entity,
        CEnemySpawner(events),
    )