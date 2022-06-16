
import tempfile

import runtime.logging.logging as logging
from typing import Optional
from containers.ContainerCache import ContainerCache
from runtime.settings.ExeSettings import ToolExeSettings
from xmltool.requirements import Requirement, CondaRequirement, ContainerRequirement
from xmltool.XMLToolDefinition import XMLToolDefinition
from containers.Container import Container
from containers.ContainerFetcher import BiocontainerFetcher, CondaBiocontainerFetcher, ContainerBiocontainerFetcher

DISABLE_CACHE = False

def fetch_container(esettings: ToolExeSettings, xmltool: XMLToolDefinition) -> Optional[Container]:
    cache: ContainerCache = load_cache(esettings.container_cachedir)
    container = fetch_from_cache(cache, xmltool)
    if not container:
        container = fetch_online(xmltool)
        if container:
            cache.add(container)
        else:      
            logging.no_container()
    return container

def fetch_from_cache(cache: ContainerCache, xmltool: XMLToolDefinition) -> Optional[Container]:
    if cache.exists(xmltool.metadata.id, xmltool.metadata.version):
        return cache.get(xmltool.metadata.id, xmltool.metadata.version)
    return None

def load_cache(cache_path: str) -> ContainerCache:
    if DISABLE_CACHE:
        temp = tempfile.TemporaryFile()
        cache_path = f'{tempfile.gettempdir()}/{temp.name}'
    return ContainerCache(cache_path)

def fetch_online(xmltool: XMLToolDefinition) -> Optional[Container]:
    main_requirement = xmltool.metadata.get_main_requirement()
    strategy = select_strategy(main_requirement)
    return strategy.fetch(
        tool_id=xmltool.metadata.id,
        tool_version=xmltool.metadata.version,
        requirement=main_requirement
    )

def select_strategy(main_requirement: Requirement) -> BiocontainerFetcher:
    match main_requirement:
        case CondaRequirement():
            return CondaBiocontainerFetcher()
        case ContainerRequirement():
            return ContainerBiocontainerFetcher()
        case _:
            raise RuntimeError()



