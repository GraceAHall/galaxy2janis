

# classes
from startup.ExeSettings import WorkflowExeSettings
from workflows.step.values.InputValue import InputValueType
from workflows.workflow.WorkflowFactory import WorkflowFactory
from workflows.workflow.Workflow import Workflow
from workflows.io.WorkflowInput import WorkflowInput
from workflows.io.WorkflowOutput import WorkflowOutput

# modules
from workflows.step.values.ValueLinker import link_step_values
from workflows.step.tools.assign import set_tools, set_tool_paths



"""
file ingests a galaxy workflow, then downloads and translates each tool
to a janis definition
"""

def parse_workflow(wsettings: WorkflowExeSettings) -> Workflow:
    workflow = init_workflow(wsettings)
    set_main_workflow_inputs(workflow)
    set_tools(wsettings, workflow)
    set_tool_paths(wsettings, workflow)
    link_step_values(workflow)
    set_step_workflow_inputs(workflow)
    set_workflow_outputs(workflow)
    return workflow

def init_workflow(wsettings: WorkflowExeSettings) -> Workflow:
    # basic parsing workflow into internal representaiton
    galaxy_workflow_path = wsettings.get_galaxy_workflow_path()
    factory = WorkflowFactory()
    workflow = factory.create(galaxy_workflow_path)
    return workflow

def set_main_workflow_inputs(workflow: Workflow) -> None:
    # each InputDataStep only has a single step input and output
    for step in workflow.list_input_steps():
        inp = step.list_inputs()[0]
        out = step.list_outputs()[0]
        #entity_info = {'name': inp.name}
        #name = TagFormatter().format(entity_info)
        new_input = WorkflowInput(
            step_id=step.metadata.step_id,
            input_name=inp.name,
            janis_datatypes=out.janis_datatypes,
            from_input_step=True
        )
        workflow.add_input(new_input)
        workflow.steps_inputs_uuid_map[step.get_uuid()] = new_input.get_uuid()

def set_step_workflow_inputs(workflow: Workflow) -> None:
    for step in workflow.list_tool_steps():
        assert(step.tool)
        for uuid, input_value in step.list_tool_values():
            if input_value.valtype == InputValueType.RUNTIME:
                # create and register new input
                component = step.tool.get_input(uuid)
                component_tag = step.tool.tag_manager.get('tool_input', uuid)
                new_input = WorkflowInput(
                    step_id=step.metadata.step_id,
                    input_name=component_tag,
                    janis_datatypes=component.janis_datatypes
                )
                workflow.add_input(new_input)
                # override input_value to be the tag of the newly created workflow input
                tag = workflow.tag_manager.get('workflow_input', new_input.get_uuid())
                input_value.value = f'w.{tag}'
                input_value.valtype = InputValueType.WORKFLOW_INPUT

def set_workflow_outputs(workflow: Workflow) -> None:
    for step in workflow.list_tool_steps():
        assert(step.tool)
        for out in step.list_outputs():
            if out.is_wflow_out:
                step_tag = workflow.tag_manager.get('workflow_step', step.get_uuid())
                workflow.add_output(WorkflowOutput(
                    step_id=step.metadata.step_id,
                    step_tag=step_tag,
                    step_output=out.name,
                    janis_datatypes=out.janis_datatypes
                ))








