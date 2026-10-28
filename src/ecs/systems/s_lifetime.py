import esper

from src.ecs.components.c_lifetime import CLifetime


def system_lifetime(world: esper.World, delta_time: float):
    for entity, c_lifetime in world.get_component(CLifetime):
        c_lifetime.remaining -= delta_time
        if c_lifetime.remaining <= 0:
            world.delete_entity(entity)
