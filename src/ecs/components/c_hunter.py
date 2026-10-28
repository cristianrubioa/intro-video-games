import pygame

class CHunter:
    def __init__(
        self,
        origin: pygame.Vector2,
        distance_start_chase: float,
        distance_start_return: float,
        velocity_chase: float,
        velocity_return: float,
        sound_chase: str
    ) -> None:
        self.origin = origin
        self.distance_start_chase = distance_start_chase
        self.distance_start_return = distance_start_return
        self.velocity_chase = velocity_chase
        self.velocity_return = velocity_return
        self.sound_chase = sound_chase
        self.is_chasing = False
