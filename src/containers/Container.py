



from dataclasses import dataclass




@dataclass
class Container: 
    tool: str = ''
    version: str = ''
    url: str = ''
    image_type: str = ''
    registry_host: str = ''