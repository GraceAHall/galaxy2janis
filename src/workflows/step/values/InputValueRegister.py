



from abc import ABC, abstractmethod
from typing import Optional, Tuple
from workflows.step.values.InputValue import ConnectionInputValue, InputValue, RuntimeInputValue, WorkflowInputInputValue




class ValueOrderingStrategy(ABC):
    @abstractmethod
    def order(self, input_values: list[Tuple[str, InputValue]]) -> list[Tuple[str, InputValue]]:
        """orders input values and returns ordered list"""
        ...

class AlphabeticalStrategy(ValueOrderingStrategy):
    def order(self, input_values: list[Tuple[str, InputValue]]) -> list[Tuple[str, InputValue]]:
        input_values.sort(key=lambda x: x[0])
        return input_values

class ComponentTypeStrategy(ValueOrderingStrategy):
    def order(self, input_values: list[Tuple[str, InputValue]]) -> list[Tuple[str, InputValue]]:
        priorities = {'positional': 0, 'flag': 1, 'option': 2}
        input_values.sort(key=lambda x: priorities[x[1].comptype])
        return input_values

class RuntimeNonRuntimeStrategy(ValueOrderingStrategy):
    def order(self, input_values: list[Tuple[str, InputValue]]) -> list[Tuple[str, InputValue]]:
        runtime = [x for x in input_values if isinstance(x[1], RuntimeInputValue)]
        non_runtime = [x for x in input_values if not isinstance(x[1], RuntimeInputValue)]
        return runtime + non_runtime

class ConnectionNonConnectionStrategy(ValueOrderingStrategy):
    def order(self, input_values: list[Tuple[str, InputValue]]) -> list[Tuple[str, InputValue]]:
        connection = [x for x in input_values if isinstance(x[1], ConnectionInputValue)]
        non_connection = [x for x in input_values if not isinstance(x[1], ConnectionInputValue)]
        return connection + non_connection

class WorkflowInputStrategy(ValueOrderingStrategy):
    def order(self, input_values: list[Tuple[str, InputValue]]) -> list[Tuple[str, InputValue]]:
        connection = [x for x in input_values if isinstance(x[1], WorkflowInputInputValue)]
        non_connection = [x for x in input_values if not isinstance(x[1], WorkflowInputInputValue)]
        return connection + non_connection



class InputValueRegister:
    def __init__(self):
        self.values: dict[str, InputValue] = {}
        self.unlinked: list[InputValue] = []
        # changing the order of the objects below changes the 
        # ordering priority, as the last ordering method has the highest impact etc
        self.value_ordering_strategies = [
            ComponentTypeStrategy(),
            AlphabeticalStrategy(),
            RuntimeNonRuntimeStrategy(),
            WorkflowInputStrategy(),
            ConnectionNonConnectionStrategy()
        ]

    def get(self, uuid: str) -> Optional[InputValue]:
        if uuid in self.values:
            return self.values[uuid]

    def update(self, uuid: str, value: InputValue) -> None:
        self.values[uuid] = value
    
    def update_unlinked(self, value: InputValue) -> None:
        self.unlinked.append(value)
    
    def list_values(self) -> list[Tuple[str, InputValue]]:
        values = list(self.values.items())
        for strategy in self.value_ordering_strategies:
            values = strategy.order(values)
        return values
    
    def list_unlinked(self) -> list[InputValue]:
        return self.unlinked

    def __str__(self) -> str:
        out_str: str = '\nInputValueRegister -----\n'
        out_str += f'{"[uuid]":>20}{"[value]":>20}{"[type]":>40}\n'
        # for uuid, input_value in self.values.items():
        #     out_str += f'{uuid:>20}{input_value.value:>20}{input_value.valtype:>40}\n'
        return out_str

