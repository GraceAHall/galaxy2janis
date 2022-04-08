


from typing import Any
from workflows.io.WorkflowInput import WorkflowInput


class InputDataStepParser:

    def parse(self, step: dict[str, Any])  -> WorkflowInput:
        return WorkflowInput(
            name=step['inputs'][0]['name'],
            step_id=step['id'],
            step_tag=None,
            gx_datatypes=step['tool_state']['format'] if 'format' in step['tool_state'] else ['file'],
            is_galaxy_input_step=True
        )


        

