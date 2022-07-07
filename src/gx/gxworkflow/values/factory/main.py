


from typing import Any
from entities.workflow.input import WorkflowInput

from shellparser.components.CommandComponent import CommandComponent

from entities.workflow import (
    ConnectionInputValue, 
    WorkflowInputInputValue,
    StaticInputValue
)
from shellparser.components.inputs.InputComponent import InputComponent

from .. import utils

def static(component: InputComponent, value: Any, default: bool=False) -> StaticInputValue:
    return StaticInputValue(
        value=value,
        _valtypestr=utils.select_input_value_type(component, value),
        comptype=utils.get_comptype(component),
        default=default
    )

def connection(component: InputComponent) -> ConnectionInputValue:
    # something about finding the step & step output
    return ConnectionInputValue(
        step_uuid=self.step_input.step_id,
        output_uuid=self.step_input.output_name,
        comptype=utils.get_comptype(component),
    )

def workflow_input(component: InputComponent, winp: WorkflowInput, is_runtime: bool=False) -> WorkflowInputInputValue:
    return WorkflowInputInputValue(
        input_uuid=winp.uuid,
        comptype=utils.get_comptype(component),
        is_runtime=is_runtime,
    )





# def default(component: CommandComponent) -> StaticInputValue:
#     strategy = DefaultInputValueFactory(component)
#     return strategy.create()

# def runtime(component: CommandComponent) -> InputValue:
#     strategy = RuntimeInputValueFactory(component)
#     return strategy.create()


# def unlinked_connection(step_input: ConnectionStepInput, workflow: Workflow) -> InputValue:
#     component = Flag(prefix='__UNKNOWN__')
#     strategy = ConnectionInputValueFactory(component, step_input, workflow)
#     return strategy.create()

# def unlinked_workflowinput(workflow_input: WorkflowInput) -> InputValue:
#     component = Flag(prefix='__UNKNOWN__')
#     strategy = WorkflowInputInputValueFactory(component, workflow_input)
#     return strategy.create()

# def cast_connection_to_workflowinput(value: ConnectionInputValue, winp: WorkflowInput) -> WorkflowInputInputValue:
#     return WorkflowInputInputValue(
#         input_uuid=winp.uuid,
#         comptype=value.comptype,
#         gxparam=value.gxparam
#     )

# # def select_strategy(component: CommandComponent, step_input: StepInput, workflow: Workflow) -> InputValueFactory:
# #     if step_input:
# #         match step_input:
# #             case ConnectionStepInput():
# #                 return ConnectionInputValueFactory(component, step_input, workflow)
# #             case RuntimeStepInput():
# #                 return RuntimeInputValueFactory(component) 
# #             case StaticStepInput():
# #                 return StaticInputValueFactory(component, step_input.value)
# #             case WorkflowInputStepInput():
# #                 workflow_input = workflow.get_input(step_id=step_input.step_id)
# #                 assert(workflow_input)
# #                 return WorkflowInputInputValueFactory(component, workflow_input)
# #             case _:
# #                 pass
# #     raise RuntimeError(f'cannot find galaxy step input for gxparam {step_input.gxvarname}')




