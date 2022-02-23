


from typing import Optional
from containers.ContainerCache import ContainerCache
from runtime.settings import ToolExeSettings
from tool.tool_definition import GalaxyToolDefinition
from containers.Container import Container
from containers.ContainerFetcher import ContainerFetcher


def fetch_container(esettings: ToolExeSettings, tool: GalaxyToolDefinition) -> Optional[Container]:
    cache: ContainerCache = load_cache(esettings)
    if cache.exists(tool.metadata.id, tool.metadata.version):
        container = cache.get(tool.metadata.id, tool.metadata.version)
    else:
        fetcher = ContainerFetcher(tool)
        container = fetcher.fetch()
        if container:
            cache.add(container)
    return container

def load_cache(esettings: ToolExeSettings) -> ContainerCache:
    cache_path = esettings.get_container_cache_path()
    return ContainerCache(cache_path)

