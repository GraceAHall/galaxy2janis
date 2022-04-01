




from command.components.CommandComponent import CommandComponent
from command.components.inputs.Option import Option
from command.components.inputs.Positional import Positional
from workflows.step.values.InputValue import InputValue, InputValueType


def update_component_from_workflow_value(component: CommandComponent, input_value: InputValue) -> None:
    # optionality
    # datatypes? only in rare cases
    update_component_optionality(component, input_value)
    #update_component_datatypes(component, input_value)

def update_component_optionality(component: CommandComponent, input_value: InputValue) -> None:
    if input_value.valtype == InputValueType.NONE:
        if isinstance(component, Option) or isinstance(component, Positional):
            component.forced_optionality = True

def update_component_datatypes(component: CommandComponent, input_value: InputValue) -> None:
    raise NotImplementedError()