


from enum import Enum, auto



class RegistryHosts(Enum):
    QUAY = auto()
    DOCKER = auto()


uri_host_map: dict[RegistryHosts, str] = {
    RegistryHosts.QUAY: 'https://quay.io/repository/biocontainers/',
    RegistryHosts.DOCKER: 'https://hub.docker.com/r/biocontainers/'
}


class ContainerNew: 
    def __init__(self):
        self.tool: str = ''
        self.version: str = ''
        self.url: str = ''
        self.image_type: str = ''
        self.host: RegistryHosts = RegistryHosts.QUAY

    def get_host_uri_prefix(self) -> str:
        return uri_host_map[self.host] 