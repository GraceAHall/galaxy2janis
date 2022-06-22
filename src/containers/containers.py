
import logs.logging as logging
import tempfile
from typing import Optional

from containers.ContainerCache import ContainerCache
from gx.xmltool.requirements import Requirement, CondaRequirement, ContainerRequirement
from gx.xmltool.XMLToolDefinition import XMLToolDefinition
from containers.Container import Container
from containers.fetching.Fetcher import Fetcher
from containers.fetching.ContainerReqFetcher import ContainerReqFetcher
#from containers.fetching.GA4GHFetcher import GA4GHFetcher
from containers.fetching.QuayIOFetcher import QuayIOFetcher

from containers.fetching.presets import get_images_preset
from containers.selection.selection import select_best_container_match
from runtime.paths import CONTAINER_CACHE

DISABLE_CACHE = False

def fetch_container(xmltool: XMLToolDefinition) -> Optional[Container]:
    requirement = xmltool.metadata.get_main_requirement()
    containers: list[Container] = []
    if not containers:
        containers = _fetch_cache(requirement)
    if not containers:
        containers = _fetch_presets(requirement)
    if not containers:
        containers = _fetch_online(requirement)
    if not containers:
        logging.no_container()
        return None
    else:
        return select_best_container_match(containers, requirement)
    
def _fetch_cache(requirement: Requirement) -> list[Container]:
    cache = _load_cache()
    return cache.get(requirement.name)

def _load_cache() -> ContainerCache:
    if DISABLE_CACHE:
        temp = tempfile.TemporaryFile()
        cache_path = f'{tempfile.gettempdir()}/{temp.name}'
    else:
        cache_path = CONTAINER_CACHE
    return ContainerCache(cache_path)

def _fetch_presets(requirement: Requirement) -> list[Container]:
    return get_images_preset(requirement)

def _fetch_online(requirement: Requirement) -> list[Container]:
    strategy = _select_strategy(requirement)
    containers = strategy.fetch(requirement)
    if containers:
        _update_cache(containers)
    return containers
    
def _select_strategy(requirement: Requirement) -> Fetcher:
    match requirement:
        case CondaRequirement():
            return QuayIOFetcher()
        #case CondaRequirement():
        #    return GA4GHFetcher()
        case ContainerRequirement():
            return ContainerReqFetcher()
        case _:
            raise RuntimeError()
    
def _update_cache(containers: list[Container]) -> None:
    cache = _load_cache()
    for container in containers: 
        cache.add(container)



