


from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from entities.workflow import WorkflowStep
    from entities.workflow import Workflow

from shellparser.components.inputs.InputComponent import InputComponent

from . import factory
import mapping

def handle_tool_default_inputs(janis: Workflow, galaxy: dict[str, Any]) -> None:
    for g_step in galaxy['steps'].values():
        if g_step['type'] == 'tool':
            j_step = mapping.step(g_step['id'], janis, galaxy)
            for component in get_linkable_components(j_step):
                input_value = factory.static(component, component.default_value, default=True)
                j_step.inputs.add(input_value)

def get_linkable_components(j_step: WorkflowStep) -> list[InputComponent]:
    # tool components which don't yet appear in register
    out: list[InputComponent] = []
    tool_inputs = j_step.tool.list_inputs()
    tool_values = j_step.inputs
    for component in tool_inputs:
        if not tool_values.get(component.uuid):
            out.append(component)
    return out
        