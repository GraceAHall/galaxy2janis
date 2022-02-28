


from abc import ABC
from dataclasses import dataclass
from typing import Any
import json

from .Components import Connection, StepInput, StepOutput, StepMetadata

@dataclass
class WorkflowStep(ABC):
    pass

@dataclass
class InputStep(WorkflowStep):
    step: int
    inputs: list[StepInput]
    optional: bool

@dataclass
class ToolStep(WorkflowStep):
    metadata: StepMetadata
    inputs: list[StepInput]
    outputs: list[StepOutput]

    def get_uri(self) -> str:
        return self.metadata.get_uri()
    
    def get_tool_name(self) -> str:
        return self.metadata.tool_name



def parse_step(step: dict[str, Any]) -> WorkflowStep:
    step['tool_state'] = json.loads(step['tool_state'])
    if step['type'] == 'data_input':
        return parse_input_step(step)
    return parse_tool_step(step)

def parse_input_step(step: dict[str, Any]) -> InputStep:
    optional: bool = False
    if step['tool_state']['optional']:
        optional = step['tool_state']['optional']
    return InputStep(
        step=step['id'],
        inputs=[make_step_input(inp) for inp in step['inputs']],
        optional=optional
    )

def parse_tool_step(step: dict[str, Any]) -> ToolStep:
    return ToolStep(
        metadata=make_step_metadata(step),
        inputs=[make_step_input(inp) for inp in step['inputs']],
        outputs=[make_step_output(inp) for inp in step['outputs']]
    )

def make_step_input(input: dict[str, str]) -> StepInput:
    return StepInput(
        input['name'],
        input['description']
    )

def make_step_output(output: dict[str, str]) -> StepOutput:
    return StepOutput(
        output['name'],
        output['type']
    )
    
def make_step_metadata(step: dict[str, Any]) -> StepMetadata:
    return StepMetadata(
        step=step['id'],
        tool_name=step['tool_shed_repository']['name'],
        owner=step['tool_shed_repository']['owner'],
        changeset_revision=step['tool_shed_repository']['changeset_revision'],
        shed=step['tool_shed_repository']['tool_shed'],
    )

