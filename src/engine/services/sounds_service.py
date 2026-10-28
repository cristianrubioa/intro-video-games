import os
import sys

import pygame


class SoundsService:
    def __init__(self) -> None:
        self._sounds = {}

    def play(self, path: str) -> None:
        path = self._resolve(path)
        if path not in self._sounds:
            self._sounds[path] = pygame.mixer.Sound(path)
        self._sounds[path].play()

    def _resolve(self, path: str) -> str:
        if sys.platform != "emscripten":
            return path
        stem, ext = path.rsplit(".", 1)
        web_path = f"{stem}-pygbag.{ext}"
        return web_path if os.path.exists(web_path) else path
