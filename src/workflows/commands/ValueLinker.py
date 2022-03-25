


from typing import Optional
from command.Command import Command
from workflows.step.Step import GalaxyWorkflowStep


class ValueLinker:
    def __init__(self, step: GalaxyWorkflowStep, command: Command):
        pass

    def link(self) -> Optional[str]:
        raise NotImplementedError()