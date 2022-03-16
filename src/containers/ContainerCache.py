




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
            galaxy_id=cdict['galaxy_id'],
            galaxy_version=cdict['galaxy_version'],
            url=cdict['url'],
            image_type=cdict['image_type'],
            registry_host=cdict['registry_host'],
            requirement_id= cdict['requirement_id'],
            requirement_version= cdict['requirement_version']
        )

    def exists(self, tool: str, version: str) -> bool:
        cache = self._load_cache()
        if tool in cache:
            if version in cache[tool]:
                return True
        return False

    def add(self, container: Container, override: bool=False):
        cache = self._load_cache()
        galaxy_id = container.galaxy_id
        galaxy_version = container.galaxy_version
        if galaxy_id not in cache:
            cache[galaxy_id] = {}
        if galaxy_version not in cache[galaxy_id]:
            cache[galaxy_id][galaxy_version] = container.__dict__
        elif override:
            cache[galaxy_id][galaxy_version] = container.__dict__
        self._write_cache(cache)

    def _load_cache(self) -> dict[str, Any]:
        with open(self.cache_path, 'r') as fp:
            return json.load(fp)

    def _write_cache(self, cache: dict[str, Any]) -> None:
        with open(self.cache_path, 'w') as fp:
            json.dump(cache, fp)

