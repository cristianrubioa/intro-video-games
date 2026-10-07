class CEnemySpawner:
    def __init__(self, events: list[dict]) -> None:
        self.elapsed = 0.0
        self.events = [{**event, "fired": False} for event in events]
