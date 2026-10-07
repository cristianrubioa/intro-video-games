import json

import pygame
import esper

from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.ecs.systems.s_enemy_spawner import system_enemy_spawner
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_rendering import system_rendering
from src.ecs.systems.s_screen_bounce import system_screen_bounce

CONFIG_DIR = "assets/cfg/cfg_00"


class GameEngine:
    def __init__(self) -> None:
        pygame.init()
        self.clock = pygame.time.Clock()
        self.is_running = False
        self.framerate = 60
        self.delta_time = 0
        self.bg_color = (0, 0, 0)
        self.enemies = {}

        self.ecs_world = esper.World()

    def run(self) -> None:
        self._create()
        self.is_running = True
        try:
            while self.is_running:
                self._calculate_time()
                self._process_events()
                self._update()
                self._draw()
        except KeyboardInterrupt:
            pass
        self._clean()

    def _create(self):
        window = self._load_json("window.json")
        self.enemies = self._load_json("enemies.json")
        level = self._load_json("level_01.json")

        self.screen = pygame.display.set_mode(
            (window["size"]["w"], window["size"]["h"]), pygame.SCALED
        )
        pygame.display.set_caption(window["title"])
        self.bg_color = (window["bg_color"]["r"], window["bg_color"]["g"], window["bg_color"]["b"])
        self.framerate = window["framerate"]

        events = [{**event, "fired": False} for event in level["enemy_spawn_events"]]
        spawner_entity = self.ecs_world.create_entity()
        self.ecs_world.add_component(
            spawner_entity,
            CEnemySpawner(events),
        )

    def _load_json(self, file_name: str):
        with open(f"{CONFIG_DIR}/{file_name}") as file:
            return json.load(file)

    def _calculate_time(self):
        self.clock.tick(self.framerate)
        self.delta_time = self.clock.get_time() / 1000.0

    def _process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

    def _update(self):
        system_enemy_spawner(self.ecs_world, self.delta_time, self.enemies)
        system_movement(self.ecs_world, self.delta_time)
        system_screen_bounce(self.ecs_world, self.screen)

    def _draw(self):
        self.screen.fill(self.bg_color)
        system_rendering(self.ecs_world, self.screen)
        pygame.display.flip()

    def _clean(self):
        pygame.quit()
