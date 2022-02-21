




import json
from typing import Any
from containers.Container import Container


class ContainerCache:
    def __init__(self, cache_path: str):
        self.cache_path = cache_path

    def get(self, tool: str, version: str) -> Container:
        """not safe. assumes entry exists. use self.exists() to check"""
        cache = self._load_cache()
        cdict = cache[tool][version]
        return Container(
            tool= cdict['tool'],
            version= cdict['version'],
            url= cdict['url'],
            image_type= cdict['image_type'],
            registry_host= cdict['registry_host'],
        )

    def exists(self, tool: str, version: str) -> bool:
        cache = self._load_cache()
        if tool in cache:
            if version in cache[tool]:
                return True
        return False

    def add(self, container: Container, override: bool=False):
        cache = self._load_cache()
        tool = container.tool
        version = container.version
        if tool not in cache:
            cache[tool] = {}
        if version not in cache[tool]:
            cache[tool][version] = container.__dict__
        elif override:
            cache[tool][version] = container.__dict__
        self._write_cache(cache)

    def _load_cache(self) -> dict[str, Any]:
        with open(self.cache_path, 'r') as fp:
            return json.load(fp)

    def _write_cache(self, cache: dict[str, Any]) -> None:
        with open(self.cache_path, 'w') as fp:
            json.dump(cache, fp)

