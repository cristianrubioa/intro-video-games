import json


class ConfigsService:
    def __init__(self) -> None:
        self._configs = {}

    def get(self, path: str) -> dict:
        if path not in self._configs:
            with open(path) as file:
                self._configs[path] = json.load(file)
        return self._configs[path]
