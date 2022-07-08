
from entities.workflow.input import WorkflowInput
from typing import Any

from entities.workflow import Workflow
from entities.workflow import (
    WorkflowInputStepInput,
    ConnectionStepInput,
    RuntimeStepInput,
    StaticStepInput
)
from ..tool_state import load_tool_state
import mapping

"""
I know this file looks hectic and is hectic to read.
Ingesting StepInputs is one of the most complex bits of the process.
Closely followed by linking values. 
will get a refactor in time. 

TODO explain what the g_target, g_emitter, j_target, j_emitter stuff is. 
"""


def ingest_workflow_steps_inputs(janis: Workflow, galaxy: dict[str, Any]) -> None:
    ingestor = StepInputIngestor(janis, galaxy)
    return ingestor.ingest()


class StepInputIngestor:
    def __init__(self, janis: Workflow, galaxy: dict[str, Any]):
        self.janis = janis
        self.galaxy = galaxy

    def ingest(self) -> None:
        for step in self.galaxy['steps'].values():
            if step['type'] == 'tool':
                self.ingest_connections(step)
                self.ingest_runtime(step)
                self.ingest_static(step)

    def ingest_connections(self, galaxy_step: dict[str, Any]) -> None:
        """
        ingest connections for this galaxy step.
        \n
        for each connection, need to know the emitting entity and the target entity.
        the emitting entity is a step output, and the target is a tool component.
        there isn't always a 1-to-1 mapping here. this is due to some galaxy params not being
        linked to a tool component. 
        """
        janis_step = mapping.step(galaxy_step['id'], self.janis, self.galaxy)
        register = janis_step.inputs
        for g_target, g_emitter in galaxy_step['input_connections'].items():
            g_target = g_target.replace('|', '.')
            j_target = mapping.tool_input(g_target, janis_step.tool)
            j_emitter = mapping.emitter(g_emitter['id'], g_emitter['output_name'], self.janis, self.galaxy)
            if isinstance(j_emitter, WorkflowInput):
                step_input = WorkflowInputStepInput(j_emitter.uuid, j_target)
            else:
                j_emitter_step = mapping.step(g_emitter['id'], self.janis, self.galaxy)
                step_input = ConnectionStepInput(j_emitter_step.uuid, j_emitter.uuid, j_target)
            register.add(step_input)

    def ingest_runtime(self, galaxy_step: dict[str, Any]) -> None:
        janis_step = mapping.step(galaxy_step['id'], self.janis, self.galaxy)
        register = janis_step.inputs
        g_targets: list[str] = [inp['name'] for inp in galaxy_step['inputs']]
        g_targets: list[str] = [inp for inp in g_targets if not register.get(inp)] # already accounted for
        for g_target in g_targets:
            g_target = g_target.replace('|', '.')
            j_target = mapping.tool_input(g_target, janis_step.tool)
            step_input = RuntimeStepInput(j_target)
            register.add(step_input)
    
    def ingest_static(self, galaxy_step: dict[str, Any]) -> None:
        janis_step = mapping.step(galaxy_step['id'], self.janis, self.galaxy)
        register = janis_step.inputs
        galaxy_step['tool_state'] = load_tool_state(galaxy_step)
        for g_target, value in galaxy_step['tool_state'].items(): #type: ignore
            g_target = g_target.replace('|', '.')
            if not register.get(g_target): # already accounted for
                if not g_target.endswith('__'): 
                    j_target = mapping.tool_input(g_target, janis_step.tool)
                    if value == 'RuntimeValue':
                        step_input = RuntimeStepInput(j_target)
                    else:
                        assert(j_target)
                        assert(j_target.gxparam)
                        step_input = StaticStepInput(j_target.gxparam, value)
                    register.add(step_input)

