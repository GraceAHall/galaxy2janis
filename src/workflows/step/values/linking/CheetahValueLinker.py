

from command.components.CommandComponent import CommandComponent
from tool.Tool import Tool
from workflows.io.WorkflowInput import WorkflowInput
from workflows.workflow.Workflow import Workflow

from workflows.step.WorkflowStep import WorkflowStep
from workflows.step.inputs.StepInput import ConnectionStepInput, WorkflowInputStepInput

from workflows.step.values.InputValueRegister import InputValueRegister
from workflows.step.values.component_updates import update_component_from_workflow_value
from workflows.step.values.InputValue import (
    DefaultInputValue, 
    InputValue, 
    InputValueType, 
    RuntimeInputValue, 
    StaticInputValue
)
import workflows.step.values.create_value as value_utils


from command.manipulation import sectional_template
from command.manipulation import resolve_aliases



class CheetahValueLinker:
    """
    - create simplified <command>
    - for each tool Flag/Option (component)
        - attempt to locate prefix
        - if located:
            determine value
        - else:
            value is None
            update component -> Optionality 

    """

    def __init__(self, step: WorkflowStep, workflow: Workflow):
        assert(step.tool)
        self.step = step
        self.tool: Tool = step.tool 
        self.workflow = workflow
        self.valregister: InputValueRegister = InputValueRegister()
        self.cmdstr: str = self.prepare_command()

    def prepare_command(self) -> str:
        assert(self.step.tool)
        cmdstr = sectional_template(
            cmdstr=self.step.tool.raw_command,
            inputs=self.step.inputs.list()
        )
        cmdstr = resolve_aliases(cmdstr)
        return cmdstr

    def link(self) -> InputValueRegister:
        raise NotImplementedError()
        














    # def link(self) -> None:
    #     # setting basic values
    #     self.assign_supplied_values()
    #     self.assign_default_values()
    #     self.assign_unlinked()
    #     self.update_component_knowledge()
    #     # adjusting values
    #     self.migrate_default_to_runtime()
    #     #self.migrate_connection_to_workflowinput()
    #     self.migrate_runtime_to_workflowinput()
    #     self.migrate_static_to_default()
    #     # cleanup
    #     self.assert_all_components_assigned()
    #     self.step.values = self.valregister

    # def assign_supplied_values(self) -> None:
    #     # link tool components to static and connection inputs
    #     tool_inputs = self.tool.list_inputs()
    #     for component in tool_inputs:
    #         if self.is_directly_linkable(component):
    #             gxvarname = component.gxparam.name  # type: ignore
    #             step_input = self.step.inputs.get(gxvarname)
    #             if step_input:
    #                 value = value_utils.create(component, step_input, self.workflow) # type: ignore
    #                 self.valregister.update_linked(component.get_uuid(), value)
    #                 step_input.linked = True
    
    # def is_directly_linkable(self, component: CommandComponent) -> bool:
    #     """
    #     checks whether a janis tool input can actually be linked to a value in the 
    #     galaxy workflow step.
    #     only possible if the component has a gxparam, and that gxparam is referenced as a
    #     ConnectionStepInput, RuntimeStepInput or StaticStepInput
    #     """
    #     if component.gxparam:
    #         query = component.gxparam.name 
    #         if self.step.inputs.get(query):
    #             return True
    #     return False
    
    # def assign_default_values(self) -> None:
    #     tool_inputs = self.tool.list_inputs()
    #     for component in tool_inputs:
    #         if not self.valregister.get_linked(component.get_uuid()):
    #             value = value_utils.create_default(component)
    #             self.valregister.update_linked(component.get_uuid(), value)
    
    # def assign_unlinked(self) -> None:
    #     # go through step inputs, checking if any have the 'linked' attribute as false
    #     permitted_inputs = [WorkflowInputStepInput, ConnectionStepInput]
    #     for step_input in self.step.inputs.list():
    #         if not step_input.linked and type(step_input) in permitted_inputs:
    #             # workflow inputs
    #             if isinstance(step_input, WorkflowInputStepInput):
    #                 workflow_input = self.workflow.get_input(step_id=step_input.step_id)
    #                 assert(workflow_input)
    #                 input_value = value_utils.create_unlinked_workflowinput(workflow_input)
    #             # step connections
    #             if isinstance(step_input, ConnectionStepInput):
    #                 input_value = value_utils.create_unlinked_connection(step_input, self.workflow)
    #             self.valregister.update_unlinked(input_value)

    # def update_component_knowledge(self) -> None:
    #     self.update_components_via_values()
    #     self.update_components_via_presence()

    # def update_components_via_values(self) -> None:
    #     for uuid, value in self.valregister.linked:
    #         component = self.tool.get_input(uuid)
    #         update_component_from_workflow_value(component, value)
    
    # def update_components_via_presence(self) -> None:
    #     """
    #     if component is not optional, but has default=None and no reference in StepInputs,
    #     mark this as optional as its not referred to anywhere. must be optional
    #     """
    #     for component in self.tool.list_inputs():
    #         comp_uuid = component.get_uuid()
    #         if not component.is_optional():
    #             value = self.valregister.get_linked(comp_uuid)
    #             if isinstance(value, DefaultInputValue) and value.valtype == InputValueType.NONE:
    #                 component.forced_optionality = True

    # def migrate_default_to_runtime(self) -> None:
    #     """
    #     swap DefaultInputValue for RuntimeInputValue for InputValues
    #     where the default doens't look right. ie environment variables
    #     forces the user to supply a value for this input. 
    #     """
    #     for uuid, value in self.valregister.linked:
    #         if self.should_migrate_default_to_runtime(value):
    #             component = self.tool.get_input(uuid)
    #             input_value = value_utils.create_runtime(component)
    #             self.valregister.update_linked(uuid, input_value)
    
    # def should_migrate_default_to_runtime(self, value: InputValue) -> bool:
    #     if isinstance(value, DefaultInputValue):
    #         if value.valtype == InputValueType.ENV_VAR:
    #             return True
    #     return False

    # def migrate_static_to_default(self) -> None:
    #     """
    #     this marks whether the value supplied should be considered the default
    #     for the tool input. can be due to value being same as tool input default,
    #     or when the input value is None
    #     """
    #     for uuid, value in self.valregister.linked:
    #         if self.should_migrate_static_to_default(uuid, value):
    #             component = self.tool.get_input(uuid)
    #             input_value = value_utils.create_default(component)
    #             self.valregister.update_linked(uuid, input_value)

    # def should_migrate_static_to_default(self, uuid: str, value: InputValue) -> bool:
    #     if isinstance(value, StaticInputValue):
    #         component = self.tool.get_input(uuid)
    #         if value.valtype == InputValueType.NONE:
    #             return True
    #         elif str(component.get_default_value()) == value.value:
    #             return True
    #     return False

    # def migrate_runtime_to_workflowinput(self) -> None:
    #     """
    #     each tool input which is a RuntimeInputValue at this stage should be converted
    #     to a WorkflowInputInputValue. A RuntimeInputValue here means that we couldn't link
    #     a StepInput to any known ToolInputs (not direcly linkable), or that the StepInput
    #     is genuinely specified as a runtimevalue in the workflow. 
    #     A WorkflowInput will be created, and the user will have to supply a value for this 
    #     input when running the workflow. 
    #     """
    #     for uuid, value in self.valregister.linked:
    #         if self.should_migrate_runtime_to_workflowinput(value):
    #             component = self.tool.get_input(uuid)
    #             workflow_input = self.create_workflow_input(uuid)
    #             self.workflow.add_input(workflow_input)
    #             input_value = value_utils.create_workflow_input(component, workflow_input)
    #             input_value.is_runtime = True
    #             self.valregister.update_linked(uuid, input_value)

    # def should_migrate_runtime_to_workflowinput(self, value: InputValue) -> bool:
    #     if isinstance(value, RuntimeInputValue):
    #         return True
    #     return False

    # def create_workflow_input(self, comp_uuid: str) -> WorkflowInput:
    #     """creates a workflow input for the tool input component"""
    #     component = self.tool.get_input(comp_uuid)
    #     component_tag = self.tool.tag_manager.get(comp_uuid)
    #     step_id = self.step.metadata.step_id
    #     step_tag = self.workflow.get_step_tag_by_step_id(step_id)
    #     return WorkflowInput(
    #         name=component_tag,
    #         step_id=step_id,
    #         step_tag=step_tag,
    #         janis_datatypes=component.janis_datatypes,
    #         is_galaxy_input_step=False
    #     )
    
    # def assert_all_components_assigned(self) -> None:
    #     tool_inputs = self.tool.list_inputs()
    #     for component in tool_inputs:
    #         if not self.valregister.get_linked(component.get_uuid()):
    #             raise AssertionError(f'tool input "{component.get_name()}" has no assigned step value')





    # def migrate_connection_to_workflowinput(self) -> None:
    #     self.migrate_conn_to_winp_linked()
    #     self.migrate_conn_to_winp_unlinked()

    # def migrate_conn_to_winp_linked(self) -> None:
    #     for comp_uuid, value in self.valregister.list_values():
    #         if self.should_migrate_connection_to_workflowinput(value):
    #             assert(isinstance(value, ConnectionInputValue))
    #             component = self.tool.get_input(comp_uuid)
    #             workflow_input = self.workflow.get_input(step_id=value.step_id)
    #             assert(workflow_input)
    #             input_value = value_utils.create_workflow_input(component, workflow_input)
    #             self.valregister.update(comp_uuid, input_value)
    
    # def migrate_conn_to_winp_unlinked(self) -> None:
    #     unlinked: list[InputValue] = []
    #     for value in self.valregister.list_unlinked():
    #         if self.should_migrate_connection_to_workflowinput(value):
    #             assert(isinstance(value, ConnectionInputValue))
    #             workflow_input = self.workflow.get_input(step_id=value.step_id)
    #             assert(workflow_input)
    #             value = value_utils.cast_connection_to_workflowinput(value, workflow_input)
    #         unlinked.append(value)
    #     self.valregister.unlinked = unlinked

    # def should_migrate_connection_to_workflowinput(self, value: InputValue) -> bool:
    #     if isinstance(value, ConnectionInputValue):
    #         step = self.workflow.steps[value.step_id]
    #         if isinstance(step, InputDataStep):
    #             return True
    #     return False