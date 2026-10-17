import json

import pygame
import esper

from src.create.prefab_creator import create_enemy_spawner
from src.create.prefab_creator import create_player_square
from src.create.prefab_creator import create_input_player

from src.ecs.systems.s_enemy_spawner import system_enemy_spawner
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_rendering import system_rendering
from src.ecs.systems.s_input_player import system_input_player
from src.ecs.systems.s_collision_player_enemy import system_collisions_player_enemy
from src.ecs.systems.s_screen_bounce import system_screen_bounce
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.c_input_command import CInputCommand
from src.ecs.components.c_input_command import CommandPhase


CONFIG_DIR = "assets/cfg/cfg_00"


class GameEngine:
    def __init__(self) -> None:
        pygame.init()
        self.clock = pygame.time.Clock()
        self.is_running = False
        self.delta_time = 0

        window = self._load_json("window.json")
        self.enemies = self._load_json("enemies.json")
        self.level = self._load_json("level_01.json")
        self.player = self._load_json("player.json")

        self.screen = pygame.display.set_mode(
            (window["size"]["w"], window["size"]["h"]), pygame.SCALED
        )
        pygame.display.set_caption(window["title"])
        self.bg_color = (window["bg_color"]["r"], window["bg_color"]["g"], window["bg_color"]["b"])
        self.framerate = window["framerate"]

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
        self.player_entity = create_player_square(self.ecs_world, self.player, self.level["player_spawn"])
        self.player_c_v = self.ecs_world.component_for_entity(self.player_entity, CVelocity)
        create_enemy_spawner(self.ecs_world, self.level)
        create_input_player(self.ecs_world)

    def _load_json(self, file_name: str):
        with open(f"{CONFIG_DIR}/{file_name}") as file:
            return json.load(file)

    def _calculate_time(self):
        self.clock.tick(self.framerate)
        self.delta_time = self.clock.get_time() / 1000.0

    def _process_events(self):
        for event in pygame.event.get():
            system_input_player(self.ecs_world, event, self._do_action)
            if event.type == pygame.QUIT:
                self.is_running = False

    def _update(self):
        system_enemy_spawner(self.ecs_world, self.delta_time, self.enemies)
        system_movement(self.ecs_world, self.delta_time)
        system_screen_bounce(self.ecs_world, self.screen)
        system_collisions_player_enemy(self.ecs_world, self.player_entity, self.level)
        self.ecs_world._clear_dead_entities()

    def _draw(self):
        self.screen.fill(self.bg_color)
        system_rendering(self.ecs_world, self.screen)
        pygame.display.flip()

    def _clean(self):
        self.ecs_world.clear_database()
        pygame.quit()

    def _do_action(self, c_input: CInputCommand):
        print(c_input.name + " " + str(c_input.phase))
        if c_input.name == "PLAYER_LEFT":
            if c_input.phase == CommandPhase.START:
                self.player_c_v.vel.x -= self.player["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self.player_c_v.vel.x += self.player["input_velocity"]
        elif c_input.name == "PLAYER_RIGHT":
            if c_input.phase == CommandPhase.START:
                self.player_c_v.vel.x += self.player["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self.player_c_v.vel.x -= self.player["input_velocity"]
        if c_input.name == "PLAYER_UP":
            if c_input.phase == CommandPhase.START:
                self.player_c_v.vel.y -= self.player["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self.player_c_v.vel.y += self.player["input_velocity"]
        elif c_input.name == "PLAYER_DOWN":
            if c_input.phase == CommandPhase.START:
                self.player_c_v.vel.y += self.player["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self.player_c_v.vel.y -= self.player["input_velocity"]
        