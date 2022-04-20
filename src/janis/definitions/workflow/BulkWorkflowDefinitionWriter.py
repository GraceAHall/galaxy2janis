


import janis.definitions.workflow.formatting as formatting

# local
from .BaseWorkflowDefinitionWriter import BaseWorkflowDefinitionWriter


class BulkWorkflowDefinitionWriter(BaseWorkflowDefinitionWriter):
    
    def write_steps(self) -> None:
        steps_str = '# STEPS'
        step_count = 0
        for step in list(self.workflow.steps.values()):
            step_count += 1
            steps_str += formatting.format_step(self.workflow, step, step_count)
        steps_str += '\n'
        self.write_to_workflow_page(steps_str)



    