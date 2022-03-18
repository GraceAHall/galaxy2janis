


from typing import Optional
from containers.ContainerCache import ContainerCache
from startup.ExeSettings import ToolExeSettings
from runtime.Logger import Logger
from xmltool.requirements import Requirement, CondaRequirement, ContainerRequirement
from xmltool.tool_definition import XMLToolDefinition
from containers.Container import Container
from containers.ContainerFetcher import BiocontainerFetcher, CondaBiocontainerFetcher, ContainerBiocontainerFetcher


def fetch_container(esettings: ToolExeSettings, logger: Logger, xmltool: XMLToolDefinition) -> Optional[Container]:
    cache: ContainerCache = load_cache(esettings.get_container_cache_path())
    tool_id = xmltool.metadata.id
    tool_version = xmltool.metadata.version
    main_requirement = xmltool.metadata.get_main_requirement()
    if cache.exists(tool_id, tool_version):
        container = cache.get(tool_id, tool_version)
    else:
        fetcher = get_fetcher(main_requirement)
        container = fetcher.fetch(
            tool_id=xmltool.metadata.id,
            tool_version=xmltool.metadata.version,
            requirement=main_requirement
        )
        if container:
            cache.add(container)
        else:            
            logger.log(1, 'no suitable container found')
    return container

def load_cache(cache_path: str) -> ContainerCache:
    return ContainerCache(cache_path)

def get_fetcher(main_requirement: Requirement) -> BiocontainerFetcher:
    match main_requirement:
        case CondaRequirement():
            return CondaBiocontainerFetcher()
        case ContainerRequirement():
            return ContainerBiocontainerFetcher()
        case _:
            raise RuntimeError()




