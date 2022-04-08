




from command.components.CommandComponent import CommandComponent
from command.components.inputs.Option import Option
from command.components.inputs.Positional import Positional
from workflows.step.values.InputValue import InputValue, StaticInputValue, InputValueType


def update_component_from_workflow_value(component: CommandComponent, input_value: InputValue) -> None:
    # optionality
    # datatypes? only in rare cases
    match input_value:
        case StaticInputValue(is_default_value=True):
            update_component_optionality(component)
        case StaticInputValue(valtype=InputValueType.NONE):
            update_component_optionality(component)
        case StaticInputValue(valtype=InputValueType.ENV_VAR):
            pass
        case _:
            pass

def update_component_optionality(component: CommandComponent) -> None:
    if isinstance(component, Option) or isinstance(component, Positional):
        component.forced_optionality = True

def update_component_datatypes(component: CommandComponent, input_value: InputValue) -> None:
    raise NotImplementedError()