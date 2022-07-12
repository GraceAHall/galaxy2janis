


from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from entities.workflow import WorkflowStep
    from entities.workflow import Workflow

from entities.workflow import WorkflowInput
from entities.workflow import InputValue
from entities.workflow import WorkflowInputInputValue

from shellparser.components.inputs.InputComponent import InputComponent

import tags
import mapping
import datatypes


def handle_tool_runtime_inputs(janis: Workflow, galaxy: dict[str, Any]) -> None:
    """runtime user inputs in step 'inputs'"""
    ingestor = RuntimeInputIngestor(janis, galaxy)
    ingestor.ingest()


class RuntimeInputIngestor:
    def __init__(self, janis: Workflow, galaxy: dict[str, Any]):
        self.janis = janis
        self.galaxy = galaxy

    def ingest(self) -> None:
        for step in self.galaxy['steps'].values():
            if step['type'] == 'tool':
                self.ingest_runtime(step)

    def ingest_runtime(self, g_step: dict[str, Any]) -> None:
        j_step = mapping.step(g_step['id'], self.janis, self.galaxy)
        g_targets = [inp['name'] for inp in g_step['inputs']]
        
        for g_target in g_targets:
            g_target = g_target.replace('|', '.')
            j_target = mapping.tool_input(g_target, j_step.tool)

            if not self.already_ingested(g_target, g_step):
                if not self.already_assigned(j_target, j_step):
                    if j_target: # TODO only care if can link
                        # create workflow input & add to workflow
                        winp = self.create_workflow_input(j_step, j_target)
                        self.janis.add_input(winp)
                        # create step value & add to step 
                        value = self.create_workflow_value(j_target, winp)
                        j_step.inputs.add(value)

    def create_workflow_input(self, j_step: WorkflowStep, j_target: InputComponent) -> WorkflowInput:
        step_tag = tags.workflow.get(j_step.uuid)
        input_tag = tags.tool.get(j_target.uuid)
        return WorkflowInput(
            name=f'{step_tag}_{input_tag}',
            array=j_target.array,
            is_galaxy_input_step=False,
            janis_datatypes=datatypes.get(j_target),
        )

    def create_workflow_value(self, j_target: InputComponent, winp: WorkflowInput) -> InputValue:
        return WorkflowInputInputValue(
            component=j_target,
            input_uuid=winp.uuid,
            is_runtime=True
        )

    def already_ingested(self, g_target: str, gstep: dict[str, Any]) -> bool:
        if g_target in gstep['input_connections']:
            return True
        return False
    
    def already_assigned(self, j_target: Optional[InputComponent], j_step: WorkflowStep) -> bool:
        if j_target:
            if j_step.inputs.get(j_target.uuid):
                return True
        return False

