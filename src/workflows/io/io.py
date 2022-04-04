




from workflows.workflow.Workflow import Workflow
from workflows.io.WorkflowInput import WorkflowInput
from workflows.io.WorkflowOutput import WorkflowOutput
from tags.TagFormatter import TagFormatter


def generate_io(workflow: Workflow) -> None:
    set_main_inputs(workflow)
    set_step_inputs(workflow)
    workflow.register_workflow_input_tags()
    migrate_runtime_values_to_workflow_inputs(workflow)
    set_outputs(workflow)
    workflow.register_workflow_output_tags()

def set_main_inputs(workflow: Workflow) -> None:
    # each InputDataStep only has a single step input and output
    for step_id, step in workflow.get_input_steps().items():
        inp = step.list_step_inputs()[0]
        out = step.list_step_outputs()[0]
        entity_info = {'name': inp.name}
        tag = TagFormatter().format(entity_info)
        workflow.inputs.append(WorkflowInput(
            step_id=step_id,
            step_tag='in',
            input_tag=tag,
            janis_datatypes=out.janis_datatypes,
            from_input_step=True
        ))

def set_step_inputs(workflow: Workflow) -> None:
    for step_tag, step in workflow.get_tool_steps().items():
        assert(step.tool)
        for name, value in step.list_tool_values():
            if value.value == 'RuntimeValue':
                step_tag = workflow.tag_manager.get('workflow_step', step.get_uuid())
                component = step.tool.get_input(name)
                workflow.inputs.append(WorkflowInput(
                    step_id=step.metadata.step_id,
                    step_tag=step_tag,
                    input_tag=name,
                    janis_datatypes=component.janis_datatypes
                ))

def migrate_runtime_values_to_workflow_inputs(workflow: Workflow) -> None:
    # TODO HERE
    for step in workflow.get_tool_steps().values():
        if 

def set_outputs(workflow: Workflow) -> None:
    for step in workflow.get_tool_steps().values():
        assert(step.tool)
        for out in step.list_step_outputs():
            if out.is_wflow_out:
                step_tag = workflow.tag_manager.get('workflow_step', step.get_uuid())
                workflow.outputs.append(WorkflowOutput(
                    source_tag=step_tag,
                    source_output=out.name,
                    janis_datatypes=out.janis_datatypes
                ))
