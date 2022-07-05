




from typing import Optional, Protocol, Any


"""
structural typing used in this file.
galaxy objects aren't always typed or well written.
better to just define what properties an object needs to 'pass' as
a GalaxyOutput
"""

class GalaxyOutput(Protocol):
    name: str
    label: str
    output_type: str
    format: Optional[str] = None
    format_source: Optional[str] = None
    metadata_source: Optional[str] = None
    dataset_collector_descriptions: list[Any] = []


