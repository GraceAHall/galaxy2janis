
import logs.logging as logging
from typing import Iterable

from entities.workflow import Workflow
from entities.workflow import WorkflowStep
from entities.workflow import ConnectionStepInput, StepInput, WorkflowInputStepInput
from entities.workflow import InputValue

from .ValueLinker import ValueLinker
from ..factory import main as factory # lol bad logic


class UnlinkedValueLinker(ValueLinker):

    def __init__(self, step: WorkflowStep, workflow: Workflow):
        super().__init__(step, workflow)
        self.permitted_inputs = [WorkflowInputStepInput, ConnectionStepInput]

    def link(self) -> None:
        register = self.step.tool_values
        for step_input in self.get_unlinked():
            invalue = self.create_invalue(step_input)
            register.update_unlinked(invalue)
            logging.unlinked_input_connection()

    def get_unlinked(self) -> Iterable[StepInput]:
        for step_input in self.step.inputs.list():
            if not step_input.linked and type(step_input) in self.permitted_inputs:
                yield step_input

    def create_invalue(self, step_input: StepInput) -> InputValue:
        # workflow inputs (genuine or runtime)
        if isinstance(step_input, WorkflowInputStepInput):
            workflow_input = self.workflow.get_input(step_id=step_input.step_id)
            assert(workflow_input)
            return factory.workflow_input(workflow_input)
        # step connections
        elif isinstance(step_input, ConnectionStepInput):
            return factory.workflow_input(step_input, self.workflow)
        else:
            raise RuntimeError()

