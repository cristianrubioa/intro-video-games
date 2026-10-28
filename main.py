#!/usr/bin/python3
"""Función Main"""
# /// script
# dependencies = [
#   "pygame-ce",
# ]
# ///
# ponytail: esper is vendored in esper/ because pygbag's PEP 723 resolver
# can't pin versions (crashes on "=="), and unpinned grabs an incompatible esper 3.x

import asyncio
from src.engine.game_engine import GameEngine

if __name__ == "__main__":
    engine = GameEngine()
    asyncio.run(engine.run())
