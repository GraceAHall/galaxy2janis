


from entities.workflow.output import WorkflowOutput
from entities.workflow.workflow import Workflow


def init_workflow_outputs(workflow: Workflow) -> Workflow:
    for step in workflow.list_steps():
        for stepout in step.outputs.list():
            if stepout.is_wflow_out:
                toolout = stepout.tool_output
                assert(toolout)
                step_tag = workflow.tag_manager.get(step.uuid)
                toolout_tag = step.tool.tag_manager.get(toolout.uuid)
                workflow_output = WorkflowOutput(
                    step_tag=step_tag,
                    toolout_tag=toolout_tag,
                    janis_datatypes=stepout.janis_datatypes
                )
                workflow.add_output(workflow_output)
    return workflow
