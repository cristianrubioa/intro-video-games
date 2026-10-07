import esper

from src.create.prefab_creator import create_square
from src.ecs.components.c_enemy_spawner import CEnemySpawner


def system_enemy_spawner(world: esper.World, delta_time: float, enemies: dict):
    components = world.get_component(CEnemySpawner)

    c_s:CEnemySpawner

    for entity, c_s in components:
        c_s.elapsed += delta_time

        for event in c_s.events:
            if not event["fired"] and event["time"] <= c_s.elapsed:
                if event["enemy_type"] not in enemies:
                    raise ValueError(f"Tipo de enemigo no definido en enemies.json: {event['enemy_type']}")
                event["fired"] = True
                create_square(world, enemies[event["enemy_type"]], event["position"])
