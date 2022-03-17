


from dataclasses import dataclass


@dataclass
class WorkflowMetadata:
    name: str
    annotation: str
    format_version: str
    tags: list[str]
    uuid: str
    version: int

    