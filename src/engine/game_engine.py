import pygame
import esper
import asyncio

from src.create.prefab_creator import create_enemy_spawner
from src.create.prefab_creator import create_player_square
from src.create.prefab_creator import create_input_player
from src.create.prefab_creator import create_bullet
from src.create.prefab_creator import create_bullet_burst
from src.create.prefab_creator import create_text

from src.ecs.systems.s_enemy_spawner import system_enemy_spawner
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_rendering import system_rendering
from src.ecs.systems.s_input_player import system_input_player
from src.ecs.systems.s_collision_player_enemy import system_collisions_player_enemy
from src.ecs.systems.s_screen_bounce import system_screen_bounce
from src.ecs.systems.s_player_bounds import system_player_bounds
from src.ecs.systems.s_bullet_bounds import system_bullet_bounds
from src.ecs.systems.s_collision_bullet_enemy import system_collision_bullet_enemy
from src.ecs.systems.s_animation import system_animation
from src.ecs.systems.s_movement_anim import system_movement_anim
from src.ecs.systems.s_hunter_state import system_hunter_state
from src.ecs.systems.s_explosion_cleanup import system_explosion_cleanup
from src.ecs.systems.s_special_cooldown_text import system_special_cooldown_text
from src.ecs.systems.s_lifetime import system_lifetime

from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_surface import CSurface
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.components.tags.c_tag_bullet_special import CTagBulletSpecial
from src.ecs.components.c_input_command import CInputCommand
from src.ecs.components.c_input_command import CommandPhase

from src.engine.service_locator import ServiceLocator


CONFIG_DIR = "assets/cfg/cfg_verif"
SPECIAL_POP_DURATION = 0.15
UI_MARGIN = 14
UI_ROW_GAP = 8


class GameEngine:
    def __init__(self) -> None:
        pygame.init()
        self.clock = pygame.time.Clock()
        self.is_running = False
        self.delta_time = 0
        self.paused = False
        self.special_cooldown_remaining = 0.0
        self.special_pop_timer = 0.0

        window = ServiceLocator.configs_service.get(f"{CONFIG_DIR}/window.json")
        self.enemies = ServiceLocator.configs_service.get(f"{CONFIG_DIR}/enemies.json")
        self.level = ServiceLocator.configs_service.get(f"{CONFIG_DIR}/level_01.json")
        self.player = ServiceLocator.configs_service.get(f"{CONFIG_DIR}/player.json")
        self.bullet = ServiceLocator.configs_service.get(f"{CONFIG_DIR}/bullet.json")
        self.explosion = ServiceLocator.configs_service.get(f"{CONFIG_DIR}/explosion.json")
        self.interface = ServiceLocator.configs_service.get(f"{CONFIG_DIR}/interface.json")

        self.screen = pygame.display.set_mode(
            (window["size"]["w"], window["size"]["h"]), pygame.SCALED
        )
        pygame.display.set_caption(window["title"])
        self.bg_color = (window["bg_color"]["r"], window["bg_color"]["g"], window["bg_color"]["b"])
        self.framerate = window["framerate"]

        self.ecs_world = esper.World()

    async def run(self) -> None:
        self._create()
        self.is_running = True
        try:
            while self.is_running:
                self._calculate_time()
                self._process_events()
                self._update()
                self._draw()
                await asyncio.sleep(0)
        except KeyboardInterrupt:
            pass
        self._clean()

    def _create(self):
        self.player_entity = create_player_square(self.ecs_world, self.player, self.level["player_spawn"])
        self.player_c_v = self.ecs_world.component_for_entity(self.player_entity, CVelocity)
        create_enemy_spawner(self.ecs_world, self.level)
        create_input_player(self.ecs_world)
        self._create_static_texts()
        self._create_pause_text()
        self._create_special_cooldown_text()

    def _create_static_texts(self):
        font_path = self.interface["font"]

        title_cfg = self.interface["texts"]["title"]
        title_font = ServiceLocator.fonts_service.get(font_path, title_cfg["size"])
        _, title_height = title_font.size(title_cfg["text"])
        create_text(self.ecs_world, title_cfg["text"], title_font, title_cfg["color"], {"x": UI_MARGIN, "y": UI_MARGIN})

        hint_cfg = self.interface["texts"]["special_hint"]
        hint_font = ServiceLocator.fonts_service.get(font_path, hint_cfg["size"])
        hint_y = UI_MARGIN + title_height + UI_ROW_GAP
        create_text(self.ecs_world, hint_cfg["text"], hint_font, hint_cfg["color"], {"x": UI_MARGIN, "y": hint_y})

    def _create_special_cooldown_text(self):
        cfg = self.interface["special_cooldown"]
        font = ServiceLocator.fonts_service.get(self.interface["font"], cfg["size"])
        self.special_cooldown_font = font
        self.special_cooldown_color = cfg["color"]
        _, value_height = font.size("100%")
        _, label_height = font.size(cfg["label"])
        value_y = self.screen.get_height() - value_height - UI_MARGIN
        label_y = value_y - label_height - UI_ROW_GAP
        create_text(self.ecs_world, cfg["label"], font, cfg["label_color"], {"x": UI_MARGIN, "y": label_y})
        self.special_cooldown_anchor = {"x": UI_MARGIN, "y": value_y}
        self.special_cooldown_entity = create_text(
            self.ecs_world, "100%", font, cfg["color"], self.special_cooldown_anchor
        )

    def _create_pause_text(self):
        pause_cfg = self.interface["texts"]["pause"]
        font = ServiceLocator.fonts_service.get(self.interface["font"], pause_cfg["size"])
        width, height = font.size(pause_cfg["text"])
        self.pause_text_center = {
            "x": (self.screen.get_width() - width) / 2,
            "y": (self.screen.get_height() - height) / 2,
        }
        self.pause_text_hidden = {"x": self.pause_text_center["x"], "y": -height - 10}
        pause_entity = create_text(self.ecs_world, pause_cfg["text"], font, pause_cfg["color"], self.pause_text_hidden)
        self.pause_text_transform = self.ecs_world.component_for_entity(pause_entity, CTransform)

    def _calculate_time(self):
        self.clock.tick(self.framerate)
        self.delta_time = self.clock.get_time() / 1000.0

    def _process_events(self):
        for event in pygame.event.get():
            system_input_player(self.ecs_world, event, self._do_action)
            if event.type == pygame.QUIT:
                self.is_running = False

    def _update(self):
        if self.paused:
            return
        system_enemy_spawner(self.ecs_world, self.delta_time, self.enemies)
        system_hunter_state(self.ecs_world, self.player_entity)
        system_movement(self.ecs_world, self.delta_time)
        
        system_movement_anim(self.ecs_world)

        system_screen_bounce(self.ecs_world, self.screen)
        system_player_bounds(self.ecs_world, self.screen)
        system_bullet_bounds(self.ecs_world, self.screen)
        system_lifetime(self.ecs_world, self.delta_time)
        system_collisions_player_enemy(self.ecs_world, self.player_entity, self.level, self.explosion)
        system_collision_bullet_enemy(self.ecs_world, self.explosion)

        system_animation(self.ecs_world, self.delta_time)
        system_explosion_cleanup(self.ecs_world)
        self.ecs_world._clear_dead_entities()

        self._update_special_cooldown()

    def _update_special_cooldown(self):
        was_ready = self.special_cooldown_remaining <= 0
        if self.special_cooldown_remaining > 0:
            self.special_cooldown_remaining = max(0.0, self.special_cooldown_remaining - self.delta_time)
        is_ready = self.special_cooldown_remaining <= 0

        if is_ready and not was_ready:
            self.special_pop_timer = SPECIAL_POP_DURATION
        elif self.special_pop_timer > 0:
            self.special_pop_timer = max(0.0, self.special_pop_timer - self.delta_time)

        pop_scale = 1.0 + 0.3 * (self.special_pop_timer / SPECIAL_POP_DURATION)
        system_special_cooldown_text(
            self.ecs_world,
            self.special_cooldown_entity,
            self.special_cooldown_font,
            self.special_cooldown_remaining,
            self.bullet["special"]["cooldown"],
            self.special_cooldown_color,
            self.special_cooldown_anchor,
            pop_scale,
        )

    def _draw(self):
        self.screen.fill(self.bg_color)
        system_rendering(self.ecs_world, self.screen)
        pygame.display.flip()

    def _clean(self):
        self.ecs_world.clear_database()
        pygame.quit()

    def _do_action(self, c_input: CInputCommand):
        if c_input.name == "PLAYER_LEFT":
            if c_input.phase == CommandPhase.START:
                self.player_c_v.vel.x -= self.player["input_velocity"]
                self._play_move_sound()
            elif c_input.phase == CommandPhase.END:
                self.player_c_v.vel.x += self.player["input_velocity"]
        elif c_input.name == "PLAYER_RIGHT":
            if c_input.phase == CommandPhase.START:
                self.player_c_v.vel.x += self.player["input_velocity"]
                self._play_move_sound()
            elif c_input.phase == CommandPhase.END:
                self.player_c_v.vel.x -= self.player["input_velocity"]
        elif c_input.name == "PLAYER_UP":
            if c_input.phase == CommandPhase.START:
                self.player_c_v.vel.y -= self.player["input_velocity"]
                self._play_move_sound()
            elif c_input.phase == CommandPhase.END:
                self.player_c_v.vel.y += self.player["input_velocity"]
        elif c_input.name == "PLAYER_DOWN":
            if c_input.phase == CommandPhase.START:
                self.player_c_v.vel.y += self.player["input_velocity"]
                self._play_move_sound()
            elif c_input.phase == CommandPhase.END:
                self.player_c_v.vel.y -= self.player["input_velocity"]
        elif c_input.name == "PLAYER_FIRE":
            if c_input.phase == CommandPhase.START:
                self._fire_bullet()
        elif c_input.name == "PLAYER_FIRE_SPECIAL":
            if c_input.phase == CommandPhase.START:
                self._fire_special_bullet()
        elif c_input.name == "TOGGLE_PAUSE":
            if c_input.phase == CommandPhase.START:
                self._toggle_pause()

    def _play_move_sound(self):
        if not self.paused:
            ServiceLocator.sounds_service.play(self.player["sound_move"])

    def _toggle_pause(self):
        self.paused = not self.paused
        target = self.pause_text_center if self.paused else self.pause_text_hidden
        self.pause_text_transform.pos = pygame.Vector2(target["x"], target["y"])

    def _fire_bullet(self):
        if len(list(self.ecs_world.get_component(CTagBullet))) >= self.level["player_spawn"]["max_bullets"]:
            return
        p_t = self.ecs_world.component_for_entity(self.player_entity, CTransform)
        p_s = self.ecs_world.component_for_entity(self.player_entity, CSurface)
        center = p_t.pos + p_s.size / 2
        direction = pygame.Vector2(pygame.mouse.get_pos()) - center
        if direction.length_squared() > 0:
            create_bullet(self.ecs_world, self.bullet, center, direction)

    def _fire_special_bullet(self):
        if self.paused or self.special_cooldown_remaining > 0:
            return
        target = self._find_active_normal_bullet()
        if target is None:
            return
        entity, c_t, c_v, c_s = target
        center = c_t.pos + c_s.size / 2
        direction = pygame.Vector2(c_v.vel)
        special_data = self.bullet["special"]
        self.ecs_world.delete_entity(entity)
        create_bullet_burst(self.ecs_world, special_data, center, direction)
        self.special_cooldown_remaining = special_data["cooldown"]

    def _find_active_normal_bullet(self):
        for entity, (c_t, c_v, c_s, _) in self.ecs_world.get_components(
            CTransform, CVelocity, CSurface, CTagBullet
        ):
            if not self.ecs_world.has_component(entity, CTagBulletSpecial):
                return entity, c_t, c_v, c_s
        return None
