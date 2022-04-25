




from abc import ABC, abstractmethod
from workflows.step.values.InputValue import ConnectionInputValue, WorkflowInputInputValue

from janis.definitions.workflow.ToolInputLine import ToolInputLine


class LineOrderingStrategy(ABC):
    @abstractmethod
    def order(self, lines: list[ToolInputLine]) -> list[ToolInputLine]:
        """orders input values and returns ordered list"""
        ...

class AlphabeticalStrategy(LineOrderingStrategy):
    def order(self, lines: list[ToolInputLine]) -> list[ToolInputLine]:
        lines.sort(key=lambda x: x.tag_and_value)
        return lines

class ComponentTypeStrategy(LineOrderingStrategy):
    def order(self, lines: list[ToolInputLine]) -> list[ToolInputLine]:
        priorities = {'positional': 0, 'flag': 1, 'option': 2}
        lines.sort(key=lambda x: priorities[x.invalue.comptype])
        return lines

class InputOrConnectionStrategy(LineOrderingStrategy):
    priority_types = [WorkflowInputInputValue, ConnectionInputValue]
    def order(self, lines: list[ToolInputLine]) -> list[ToolInputLine]:
        top = [x for x in lines if type(x.invalue) in self.priority_types]
        bottom = [x for x in lines if type(x.invalue) not in self.priority_types]
        return top + bottom

class ConnectionNonConnectionStrategy(LineOrderingStrategy):
    def order(self, lines: list[ToolInputLine]) -> list[ToolInputLine]:
        raise NotImplementedError()
        # connection = [x for x in input_values if isinstance(x[1], ConnectionInputValue)]
        # non_connection = [x for x in input_values if not isinstance(x[1], ConnectionInputValue)]
        # return connection + non_connection

class WorkflowInputStrategy(LineOrderingStrategy):
    def order(self, lines: list[ToolInputLine]) -> list[ToolInputLine]:
        raise NotImplementedError()
        # connection = [x for x in input_values if isinstance(x[1], WorkflowInputInputValue)]
        # non_connection = [x for x in input_values if not isinstance(x[1], WorkflowInputInputValue)]
        # return connection + non_connection


# changing the order of the objects below changes the 
# ordering priority, as the last ordering method has the highest impact etc
STRATEGIES = [
    ComponentTypeStrategy(),
    AlphabeticalStrategy(),
    InputOrConnectionStrategy(),
    # WorkflowInputStrategy(),
    # ConnectionNonConnectionStrategy()
]

def order(lines: list[ToolInputLine]) -> list[ToolInputLine]:
    for strategy in STRATEGIES:
        lines = strategy.order(lines)
    return lines