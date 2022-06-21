

from typing import Optional
from dataclasses import dataclass, field


@dataclass
class Container: 
    galaxy_id: str
    galaxy_version: str
    url: str = field(repr=False)
    image_type: str = field(repr=False)
    registry_host: str = field(repr=False)
    requirement_id: Optional[str] = field(repr=False, default=None)
    requirement_version: Optional[str] = field(repr=False, default=None)