




from abc import ABC, abstractmethod
from workflows.entities.step.tool_values import ConnectionInputValue, WorkflowInputInputValue

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

class WorkflowInputPriorityStrategy(LineOrderingStrategy):
    def order(self, lines: list[ToolInputLine]) -> list[ToolInputLine]:
        top = [x for x in lines if isinstance(x.invalue, WorkflowInputInputValue)]
        bottom = [x for x in lines if not isinstance(x.invalue, WorkflowInputInputValue)]
        return top + bottom

class RuntimeInputPriorityStrategy(LineOrderingStrategy):
    def order(self, lines: list[ToolInputLine]) -> list[ToolInputLine]:
        top: list[ToolInputLine] = []
        bottom: list[ToolInputLine] = []
        for line in lines:
            if isinstance(line.invalue, WorkflowInputInputValue) and not line.invalue.is_runtime:
                top.append(line)
            else:
                bottom.append(line)
        return top + bottom

class ConnectionPriorityStrategy(LineOrderingStrategy):
    def order(self, lines: list[ToolInputLine]) -> list[ToolInputLine]:
        top = [x for x in lines if isinstance(x.invalue, ConnectionInputValue)]
        bottom = [x for x in lines if not isinstance(x.invalue, ConnectionInputValue)]
        return top + bottom


# changing the order of the objects below changes the 
# ordering priority, as the last ordering method has the highest impact etc
STRATEGIES = [
    AlphabeticalStrategy(),
    ComponentTypeStrategy(),
    RuntimeInputPriorityStrategy(),
    WorkflowInputPriorityStrategy(),
    ConnectionPriorityStrategy(),
]

def order(lines: list[ToolInputLine]) -> list[ToolInputLine]:
    for strategy in STRATEGIES:
        lines = strategy.order(lines)
    return lines