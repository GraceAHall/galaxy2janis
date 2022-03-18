




"""
Need:
workflow step
command string text -> DynamicCommandString.get_constant_text()
Command() components


objective:
for each Positional:
    assert not flag or something
    set the value

for each Flag:
    if it's in the constant text, assign True
    if not, assign default value (Flag.get_default_value())

for each Option:
    if the prefix is in the constant text:
        if there is a value (Positional) next:
            if the value is not env_var:
                assign value
            elif value is in the Step StaticStepInputs:
                assign value
            else:
                pass
    assign default value (Positional.get_default_value())

"""

from command.Command import Command
from workflows.step.Step import WorkflowStep


class ValueLinker:
    def __init__(self, step: WorkflowStep, command: Command)

    def link(self) -> 