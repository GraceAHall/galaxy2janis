

from typing import Any, Optional
from entities.tool.Tool import Tool

from entities.workflow import Workflow
from entities.workflow import WorkflowInput
from entities.workflow import WorkflowStep
from entities.workflow import StepOutput
from shellparser.components.inputs.InputComponent import InputComponent
from shellparser.components.outputs.OutputComponent import OutputComponent


# split this file into mapping.workflow, mapping.tool?

def tool_input(galaxy_param_name: str, tool: Tool) -> Optional[InputComponent]:
    for inp in tool.list_inputs():
        if inp.gxparam and inp.gxparam.name == galaxy_param_name:
            return inp

def tool_output(galaxy_param_name: str, tool: Tool) -> Optional[OutputComponent]:
    for out in tool.list_outputs():
        if out.gxparam and out.gxparam.name == galaxy_param_name:
            return out

def emitter(query_id: str, query_output: str, janis: Workflow, galaxy: dict[str, Any]) -> StepOutput | WorkflowInput:
    for g_step in galaxy['steps'].values():
        if g_step['id'] == query_id:
            if g_step['type'] == 'tool':
                j_step = _get_janis_step(query_id, janis)
                return _get_janis_step_output(query_output, j_step, g_step)
            else:
                return _get_janis_w_input(query_id, janis, galaxy)
    raise RuntimeError()

def step(query_id: str, janis: Workflow, galaxy: dict[str, Any]) -> WorkflowStep:
    """lookup the corresponding janis step for a galaxy step with id=query_id"""
    for step in galaxy['steps'].values():
        if step['id'] == query_id:
            if 'janis_uuid' not in step:
                raise RuntimeError('Galaxy step not linked to janis step')
            janis_step_uuid = step['janis_uuid']
            return _get_janis_step(janis_step_uuid, janis)
    raise RuntimeError(f'No janis step for galaxy step {query_id}')


def _get_janis_w_input(query_id: str, janis: Workflow, galaxy: dict[str, Any]) -> WorkflowInput:
    for step in galaxy['steps'].values():
        if step['id'] == query_id:
            for inp in janis.inputs:
                if inp.uuid == step['janis_uuid']:
                    return inp
    raise RuntimeError(f'No janis workflow input with uuid {query_id}')

def _get_janis_step(query_uuid: str, janis: Workflow) -> WorkflowStep:
    for step in janis.steps:
        if step.uuid == query_uuid:
            return step
    raise RuntimeError(f'No janis step with uuid {query_uuid}')

def _get_janis_step_output(query_output: str, j_step: WorkflowStep, g_step: dict[str, Any]) -> StepOutput:
    """sorry"""
    j_outs = j_step.outputs.list()
    g_outs = g_step['outputs']
    for out in g_outs:
        if out['name'] == query_output:
            for output in j_outs:
                if output.uuid == out['janis_uuid']:
                    return output
    raise RuntimeError(f'No janis step output for galaxy step output {query_output}')



