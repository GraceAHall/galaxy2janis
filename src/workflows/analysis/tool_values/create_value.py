


from typing import Any

from command.components.CommandComponent import CommandComponent
from command.components.inputs.Flag import Flag

from workflows.entities.workflow.workflow import Workflow
from workflows.entities.workflow.input import WorkflowInput

from workflows.entities.step.inputs import (
    ConnectionStepInput, 
    RuntimeStepInput, 
    StaticStepInput, 
    StepInput,
    WorkflowInputStepInput
)

from workflows.entities.step.tool_values import (
    InputValue, 
    ConnectionInputValue, 
    WorkflowInputInputValue
)

from .InputValueFactory import (
    InputValueFactory,
    ConnectionInputValueFactory,
    RuntimeInputValueFactory,
    StaticInputValueFactory,
    DefaultInputValueFactory,
    WorkflowInputInputValueFactory
)


def create(component: CommandComponent, step_input: StepInput, workflow: Workflow) -> InputValue:
    strategy = select_strategy(component, step_input, workflow)
    value = strategy.create()
    return value

def create_static(component: CommandComponent, value: Any) -> InputValue:
    strategy = StaticInputValueFactory(component, value)
    return strategy.create()

def create_default(component: CommandComponent) -> InputValue:
    strategy = DefaultInputValueFactory(component)
    return strategy.create()

def create_runtime(component: CommandComponent) -> InputValue:
    strategy = RuntimeInputValueFactory(component)
    return strategy.create()

def create_workflow_input(component: CommandComponent, workflow_input: WorkflowInput) -> WorkflowInputInputValue:
    strategy = WorkflowInputInputValueFactory(component, workflow_input)
    return strategy.create()

def create_unlinked_connection(step_input: ConnectionStepInput, workflow: Workflow) -> InputValue:
    component = Flag(prefix='__UNKNOWN__')
    strategy = ConnectionInputValueFactory(component, step_input, workflow)
    return strategy.create()

def create_unlinked_workflowinput(workflow_input: WorkflowInput) -> InputValue:
    component = Flag(prefix='__UNKNOWN__')
    strategy = WorkflowInputInputValueFactory(component, workflow_input)
    return strategy.create()

def cast_connection_to_workflowinput(value: ConnectionInputValue, winp: WorkflowInput) -> WorkflowInputInputValue:
    return WorkflowInputInputValue(
        input_uuid=winp.uuid,
        comptype=value.comptype,
        gxparam=value.gxparam
    )

def select_strategy(component: CommandComponent, step_input: StepInput, workflow: Workflow) -> InputValueFactory:
    if step_input:
        match step_input:
            case ConnectionStepInput():
                return ConnectionInputValueFactory(component, step_input, workflow)
            case RuntimeStepInput():
                return RuntimeInputValueFactory(component) 
            case StaticStepInput():
                return StaticInputValueFactory(component, step_input.value)
            case WorkflowInputStepInput():
                workflow_input = workflow.get_input(step_id=step_input.step_id)
                assert(workflow_input)
                return WorkflowInputInputValueFactory(component, workflow_input)
            case _:
                pass
    raise RuntimeError(f'cannot find galaxy step input for gxparam {step_input.gxvarname}')




