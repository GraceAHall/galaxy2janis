



from dataclasses import dataclass
from typing import Optional




@dataclass
class Container: 
    galaxy_id: str 
    galaxy_version: str
    url: str
    image_type: str
    registry_host: str
    requirement_id: Optional[str] = None
    requirement_version: Optional[str] = None