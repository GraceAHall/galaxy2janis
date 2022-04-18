




from workflows.io.WorkflowOutput import WorkflowOutput
from workflows.workflow.Workflow import Workflow


def set_outputs(workflow: Workflow) -> None:
    for step in workflow.list_steps():
        for stepout in step.list_outputs():
            if stepout.is_wflow_out:
                toolout = stepout.tool_output
                assert(step.tool)
                assert(toolout)
                step_tag = workflow.tag_manager.get(step.get_uuid())
                toolout_tag = step.tool.tag_manager.get(toolout.get_uuid())
                workflow_output = WorkflowOutput(
                    step_tag=step_tag,
                    toolout_tag=toolout_tag,
                    janis_datatypes=stepout.janis_datatypes
                )
                workflow.add_output(workflow_output)
