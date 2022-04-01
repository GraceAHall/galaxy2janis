



from abc import ABC, abstractmethod
from typing import Optional, Tuple
from workflows.step.inputs.StepInput import StepInput
from workflows.step.values.InputValue import InputValue, InputValueType




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
        runtime = [x for x in input_values if x[1].valtype == InputValueType.RUNTIME]
        non_runtime = [x for x in input_values if x[1].valtype != InputValueType.RUNTIME]
        return runtime + non_runtime

class ConnectionNonConnectionStrategy(ValueOrderingStrategy):
    def order(self, input_values: list[Tuple[str, InputValue]]) -> list[Tuple[str, InputValue]]:
        connection = [x for x in input_values if x[1].valtype == InputValueType.CONNECTION]
        non_connection = [x for x in input_values if x[1].valtype != InputValueType.CONNECTION]
        return connection + non_connection



class InputValueRegister:
    def __init__(self):
        self.values: dict[str, InputValue] = {}
        self.unlinked: list[StepInput] = []
        # changing the order of the objects below changes the 
        # ordering priority, as the last ordering method has the highest impact etc
        self.ordering_strategies = [
            ComponentTypeStrategy(),
            AlphabeticalStrategy(),
            RuntimeNonRuntimeStrategy(),
            ConnectionNonConnectionStrategy()
        ]

    def get(self, query: str) -> Optional[InputValue]:
        if query in self.values:
            return self.values[query]

    def update(self, tag: str, value: InputValue) -> None:
        self.values[tag] = value
    
    def update_unlinked(self, step_input: StepInput) -> None:
        self.unlinked.append(step_input)
    
    def list_values(self) -> list[Tuple[str, InputValue]]:
        values = list(self.values.items())
        for strategy in self.ordering_strategies:
            values = strategy.order(values)
        return values

    def __str__(self) -> str:
        out_str: str = '\nInputValueRegister -----\n'
        out_str += f'{"[tag]":>20}{"[value]":>20}{"[type]":>40}\n'
        for tag, input_value in self.values.items():
            out_str += f'{tag:>20}{input_value.value:>20}{input_value.valtype:>40}\n'
        return out_str






"""
    def get_values(self) -> dict[str, Any]:
        out: dict[str, list[Tuple[str, InputValue]]] = {
            'positional': [],
            'flag': [],
            'option': []
        }
        # yes, we can check input component type based on tag. 
        for tag, inputval in self.input_values.items():
            out[self.get_component_type(tag)].append((tag, inputval))


        out['positional'] = self.get_positional_values()

        self.order_input_value_dict(out)
        return out
    
    def order_input_value_dict(self, out: dict[str, list[Tuple[str, InputValue]]]) -> None:
        for component_type, input_values in out.items():
            out[component_type] = self.order_values(input_values)

    def order_values(self, input_values: list[Tuple[str, InputValue]]) -> list[Tuple[str, InputValue]]:
        runtime_inputs = self.get_runtime_input_values(input_values)
        non_runtime_inputs = self.get_nonruntime_input_values(input_values)
        non_runtime_inputs.sort(key=lambda x: x[0])  # sort non runtime inputs alphabetically based on name
        return runtime_inputs + non_runtime_inputs

    def get_runtime_input_values(self, input_values: list[Tuple[str, InputValue]]) -> list[Tuple[str, InputValue]]:
        out: list[Tuple[str, InputValue]] = []
        for tag, inputval in input_values:
            if inputval.valtype == InputValueType.RUNTIME_VALUE:
                out.append((tag, inputval))
        return out
    
    def get_nonruntime_input_values(self, input_values: list[Tuple[str, InputValue]]) -> list[Tuple[str, InputValue]]:
        out: list[Tuple[str, InputValue]] = []
        for tag, inputval in input_values:
            if inputval.valtype != InputValueType.RUNTIME_VALUE:
                out.append((tag, inputval))
        return out

"""

"""
step.input_values = {
    'Supplied': {
        tool.input1: val,
        tool.input2: val,
        tool.input3: val
    },
    'Runtime': [
        tool.input4,
        tool.input5,
        tool.input6,
    ],
    'Default': [
        tool.input7,
        tool.input8,
        tool.input9,
    ]
}

step.unlinked_connections = {
    ConnectionInput.name: gxparam,
    ConnectionInput.name: gxparam,
    ConnectionInput.name: gxparam
}

"""