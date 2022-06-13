


from abc import ABC
from dataclasses import dataclass


@dataclass
class Message(ABC):
    text: str

@dataclass
class WorkflowMessage(Message):
    pass

@dataclass
class StepMessage(Message):
    pass

@dataclass
class ToolMessage(Message):
    pass


class MessageOrchestrator:
    def __init__(self):
        self.messages: list[Message]