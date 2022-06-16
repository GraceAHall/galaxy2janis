



from dataclasses import dataclass
from typing import Optional


@dataclass
class JanisDatatype:
    format: str
    source: str
    classname: str
    extensions: Optional[str]
    import_path: str