


from abc import ABC, abstractmethod
from typing import Tuple
from entities.workflow.step.inputs import ConnectionInputValue, InputValue, WorkflowInputInputValue

from command import Flag
from command import Option
from command import Positional

import tags


def order_positionals(positionals: list[Positional]) -> list[Positional]:
    positionals.sort(key=lambda x: x.cmd_pos)
    return positionals

def order_flags(flags: list[Flag]) -> list[Flag]:
    flags.sort(key=lambda x: tags.tool.get(x.uuid))
    return flags

def order_options(options: list[Option]) -> list[Option]:
    options.sort(key=lambda x: tags.tool.get(x.uuid))
    return options

def order_imports(imports: list[Tuple[str, str]]) -> list[Tuple[str, str]]:
    imports = _order_imports_alphabetical(imports)
    imports = _order_imports_length(imports)
    return imports

def _order_imports_length(imports: list[Tuple[str, str]]) -> list[Tuple[str, str]]:
    imports.sort(key=lambda x: len(x[0] + x[1]), reverse=True)
    return imports

def _order_imports_alphabetical(imports: list[Tuple[str, str]]) -> list[Tuple[str, str]]:
    imports.sort(key=lambda x: f'from {x[0]} import {x[1]}')
    return imports




### INPUT VALUES ###

class InputOrderingStrategy(ABC):
    @abstractmethod
    def order(self, invalues: list[InputValue]) -> list[InputValue]:
        """orders input values and returns ordered list"""
        ...

class AlphabeticalStrategy(InputOrderingStrategy):
    def order(self, invalues: list[InputValue]) -> list[InputValue]:
        invalues.sort(key=lambda x: x.tag_and_value)
        return invalues

class CmdPosStrategy(InputOrderingStrategy):
    def order(self, invalues: list[InputValue]) -> list[InputValue]:
        top = [x for x in invalues if x.component]
        bottom = [x for x in invalues if not x.component]
        top.sort(key=lambda x: x.component.cmd_pos) # type: ignore
        return top + bottom

class RuntimeInputPriorityStrategy(InputOrderingStrategy):
    def order(self, invalues: list[InputValue]) -> list[InputValue]:
        invalues.sort(key=lambda x: isinstance(x, WorkflowInputInputValue) and x.is_runtime, reverse=True)
        return invalues

class WorkflowInputPriorityStrategy(InputOrderingStrategy):
    def order(self, invalues: list[InputValue]) -> list[InputValue]:
        invalues.sort(key=lambda x: isinstance(x, WorkflowInputInputValue), reverse=True)
        return invalues

class ConnectionPriorityStrategy(InputOrderingStrategy):
    def order(self, invalues: list[InputValue]) -> list[InputValue]:
        invalues.sort(key=lambda x: isinstance(x, ConnectionInputValue), reverse=True)
        return invalues

class UnlinkedPriorityStrategy(InputOrderingStrategy):
    def order(self, invalues: list[InputValue]) -> list[InputValue]:
        invalues.sort(key=lambda x: x.component is not None)
        return invalues


# changing the order of the objects below changes the 
# ordering priority, as the last ordering method has the highest impact etc
STRATEGIES = [
    AlphabeticalStrategy(),
    CmdPosStrategy(),
    RuntimeInputPriorityStrategy(),
    WorkflowInputPriorityStrategy(),
    ConnectionPriorityStrategy(),
    UnlinkedPriorityStrategy()
]

def order_step_inputs(invalues: list[InputValue]):
    for strategy in STRATEGIES:
        invalues = strategy.order(invalues)
    return invalues