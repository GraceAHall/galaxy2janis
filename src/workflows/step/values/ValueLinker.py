

from command.components.CommandComponent import CommandComponent
from tool.Tool import Tool
from workflows.step.Step import ToolStep
from workflows.step.inputs.StepInput import ConnectionStepInput
from workflows.step.values.InputValue import InputValue, InputValueType
from workflows.step.values.InputValueFactory import InputValueFactory
from workflows.step.values.InputValueRegister import InputValueRegister
from workflows.workflow.Workflow import Workflow
from workflows.step.values.component_updates import update_component_from_workflow_value

# module entry
def link_step_values(workflow: Workflow):
    for step in workflow.list_tool_steps():
        assert(step.tool)
        # assign actual Param objects to gxparam field of inputs
        step.input_register.assign_gxparams(step.tool)  
        linker = ValueLinker(step, workflow)
        linker.link()


class ValueLinker:
    def __init__(self, step: ToolStep, workflow: Workflow):
        self.step = step
        self.tool: Tool = step.tool # type: ignore
        self.workflow = workflow
        self.valregister: InputValueRegister = InputValueRegister()
        self.factory = InputValueFactory()

    def link(self) -> None:
        # step values
        self.assign_supplied_values()
        self.update_linked_component_knowledge()
        # default values
        self.assign_default_values()
        self.migrate_defaults_to_runtime()
        self.annotate_supplied_values_as_default()
        # cleanup
        self.assign_unlinked_connections()
        self.assert_all_components_assigned()
        print(self.valregister)
        self.step.values = self.valregister

    ### OPERATIONS

    def assign_supplied_values(self) -> None:
        # link tool components to static and connection inputs
        tool_inputs = self.tool.list_inputs()
        for component in tool_inputs:
            if self.is_directly_linkable(component):
                query = component.gxparam.name  # type: ignore
                step_input = self.step.get_input(query)
                if step_input:
                    step_input.linked = True
                    value = self.factory.create(component, step_input, self.workflow) # type: ignore
                    self.valregister.update(component.get_uuid(), value)

    def update_linked_component_knowledge(self) -> None:
        for uuid, value in self.valregister.list_values():
            component = self.tool.get_input(uuid)
            update_component_from_workflow_value(component, value)
    
    def assign_default_values(self) -> None:
        tool_inputs = self.tool.list_inputs()
        for component in tool_inputs:
            if self.should_assign_default(component):
                value = self.factory.create_default(component)
                self.valregister.update(component.get_uuid(), value)

    def migrate_defaults_to_runtime(self) -> None:
        for uuid, value in self.valregister.list_values():
            if self.should_migrate(value):
                component = self.tool.get_input(uuid)
                new_value = self.factory.create_runtime(component)
                self.valregister.update(uuid, new_value)
    
    def annotate_supplied_values_as_default(self) -> None:
        for uuid, value in self.valregister.list_values():
            if self.should_annotate_default(uuid, value):
                value.is_default_value = True
    
    def assign_unlinked_connections(self) -> None:
        for step_input in self.step.list_inputs():
            if isinstance(step_input, ConnectionStepInput) and not step_input.linked:
                input_value = self.factory.create_unlinked_connection(step_input, self.workflow)
                # in case the connection is to an InputDataStep which has been migrated to WorkflowInput
                connected_step = self.workflow.steps[step_input.step_id]
                connection_uuid = connected_step.get_uuid()
                if connection_uuid in self.workflow.steps_inputs_uuid_map:
                    workflow_input_uuid = self.workflow.steps_inputs_uuid_map[connection_uuid]
                    input_tag = self.workflow.tag_manager.get('workflow_input', workflow_input_uuid)
                    input_value.value = f'w.{input_tag}'
                self.valregister.update_unlinked(input_value)

    def assert_all_components_assigned(self) -> None:
        tool_inputs = self.tool.list_inputs()
        for component in tool_inputs:
            if not self.valregister.get(component.get_uuid()):
                raise AssertionError(f'tool input "{component.get_name()}" has no assigned step value')

    ### CHECKS

    def is_directly_linkable(self, component: CommandComponent) -> bool:
        """
        checks whether a janis tool input can actually be linked to a value in the 
        galaxy workflow step.
        only possible if the component has a gxparam, and that gxparam is referenced as a
        ConnectionStepInput, RuntimeStepInput or StaticStepInput
        """
        if component.gxparam:
            query = component.gxparam.name 
            if self.step.get_input(query):
                return True
        return False
    
    def should_assign_default(self, component: CommandComponent) -> bool:
        if not self.valregister.get(component.get_uuid()):
            return True
        return False
    
    def should_migrate(self, input_value: InputValue) -> bool:
        if input_value.valtype == InputValueType.ENV_VAR:
            return True
        return False
    
    def should_annotate_default(self, uuid: str, input_value: InputValue) -> bool:
        component = self.tool.get_input(uuid)
        if str(component.get_default_value()) == input_value.value:
            return True
        return False



