

import os

import janis.definitions.workflow.formatting as formatting
from workflows.step.WorkflowStep import WorkflowStep

# local
from .BaseWorkflowDefinitionWriter import BaseWorkflowDefinitionWriter


class StepwiseWorkflowDefinitionWriter(BaseWorkflowDefinitionWriter):
    
    def write_steps(self) -> None:
        steps_str = '# STEPS'
        step_count = 0
        for step in list(self.workflow.steps.values()):
            step_count += 1
            steps_str += formatting.format_step(self.workflow, step, step_count)
            self.write_to_step_page(step, steps_str)
    
    def write_to_step_page(self, step: WorkflowStep, contents: str) -> None:
        filepath = self.get_step_page_path(step)
        with open(filepath, 'w') as fp:
            fp.write(contents)

    def get_step_page_path(self, step: WorkflowStep) -> str:
        steps_dir = self.esettings.get_janis_steps_dir()
        step_tag = self.workflow.tag_manager.get(step.get_uuid())
        return os.path.join(steps_dir, step_tag)

    