


from dataclasses import dataclass

@dataclass
class StepMetadata:
    step: int
    tool_name: str
    owner: str
    changeset_revision: str
    shed: str

    def get_uri(self) -> str:
        return f'https://{self.shed}/repos/{self.owner}/{self.tool_name}/archive/{self.changeset_revision}.tar.gz'

@dataclass
class StepInput:
    name: str
    description: str

@dataclass
class StepOutput:
    name: str
    type: str

@dataclass
class ConnectionSource:
    step: int
    value: str
    ftype: str

@dataclass
class ConnectionDest:
    step: int
    value: str
    ftype: str

@dataclass
class Connection:
    source: ConnectionSource
    dest: ConnectionDest