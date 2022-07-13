


from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from entities.workflow import Workflow

from entities.workflow import WorkflowInput
from entities.workflow import ConnectionInputValue
from entities.workflow import WorkflowInputInputValue

import mapping


def handle_tool_connection_inputs(janis: Workflow, galaxy: dict[str, Any]) -> None:
    """connections listed in step 'input_connections'"""
    ingestor = ConnectionInputIngestor(janis, galaxy)
    ingestor.ingest()


class ConnectionInputIngestor:
    def __init__(self, janis: Workflow, galaxy: dict[str, Any]):
        self.janis = janis
        self.galaxy = galaxy

    def ingest(self) -> None:
        for step in self.galaxy['steps'].values():
            if step['type'] == 'tool':
                self.ingest_connections(step)

    def ingest_connections(self, g_step: dict[str, Any]) -> None:
        """
        ingest connections for this galaxy step.
        \n
        for each connection, need to know the emitting entity and the target entity.
        the emitting entity is a step output, and the target is a tool component.
        there isn't always a 1-to-1 mapping here. this is due to some galaxy params not being
        linked to a tool component. 
        
        j_emitter:  StepOutput or WorkflowInput (the source of the connection)
        j_target: a Tool InputComponent (the destination of the connection)

        """
        j_step = mapping.step(g_step['id'], self.janis, self.galaxy)
        for g_target, g_emitter in g_step['input_connections'].items():
            g_target = g_target.replace('|', '.')
            j_target = mapping.tool_input(g_target, j_step.tool)
            j_emitter = mapping.emitter(g_emitter['id'], g_emitter['output_name'], self.janis, self.galaxy)

            if isinstance(j_emitter, WorkflowInput):
                value = WorkflowInputInputValue(
                    component=j_target, # j_target can be InputComponent or None
                    input_uuid=j_emitter.uuid,
                    is_runtime=False
                )
            else:
                value = ConnectionInputValue(
                    component=j_target,
                    output_uuid=j_emitter.uuid
                )

            j_step.inputs.add(value)