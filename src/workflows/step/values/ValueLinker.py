

from command.components.CommandComponent import CommandComponent
from workflows.step.Step import ToolStep
from workflows.step.values.InputValue import InputValue, InputValueType
from workflows.step.values.InputValueFactory import InputValueFactory
from workflows.step.values.InputValueRegister import InputValueRegister
from workflows.workflow.Workflow import Workflow
from workflows.step.values.component_updates import update_component_from_workflow_value

# module entry
def link_step_values(workflow: Workflow):
    for step in workflow.get_tool_steps().values():
        assert(step.tool)
        # assign actual Param objects to gxparam field of inputs
        step.input_register.assign_gxparams(step.tool)  
        linker = ValueLinker(step, workflow)
        linker.link()


class ValueLinker:
    def __init__(self, step: ToolStep, workflow: Workflow):
        self.step = step
        self.workflow = workflow
        self.register: InputValueRegister = InputValueRegister()
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
        print(self.register)
        self.step.values = self.register

    ### OPERATIONS

    def assign_supplied_values(self) -> None:
        # link tool components to static and connection inputs
        assert(self.step.tool)
        tool_inputs = self.step.get_tool_inputs().values()
        for component in tool_inputs:
            if self.is_directly_linkable(component):
                tag = self.step.tool.tag_manager.get('tool_component', component.get_uuid())
                query = component.gxparam.name  # type: ignore
                step_input = self.step.input_register.get(query)
                value = self.factory.create(component, step_input, self.workflow) # type: ignore
                self.register.update(tag, value)

    def update_linked_component_knowledge(self) -> None:
        tool_input_values = self.register.list_values()
        for tag, value in tool_input_values:
            component = self.step.get_tool_input(tag)
            update_component_from_workflow_value(component, value)
    
    def assign_default_values(self) -> None:
        assert(self.step.tool)
        tool_inputs = self.step.get_tool_inputs().values()
        for component in tool_inputs:
            if self.should_assign_default(component):
                tag = self.step.tool.tag_manager.get('tool_component', component.get_uuid())
                value = self.factory.create_default(component)
                self.register.update(tag, value)

    def migrate_defaults_to_runtime(self) -> None:
        tool_input_values = self.register.list_values()
        for tag, value in tool_input_values:
            if self.should_migrate(value):
                component = self.step.get_tool_input(tag)
                new_value = self.factory.create_runtime(component)
                self.register.update(tag, new_value)
    
    def annotate_supplied_values_as_default(self) -> None:
        tool_input_values = self.register.list_values()
        for tag, value in tool_input_values:
            if self.should_annotate_default(tag, value):
                value.is_default_value = True
    
    def assign_unlinked_connections(self) -> None:
        step_inputs = self.step.input_register.list_inputs()
        for step_input in step_inputs:
            if not step_input.linked:
                self.register.update_unlinked(step_input)

    def assert_all_components_assigned(self) -> None:
        assert(self.step.tool)
        tool_inputs = self.step.get_tool_inputs().values()
        for component in tool_inputs:
            tag = self.step.tool.tag_manager.get('tool_component', component.get_uuid())
            if not self.register.get(tag):
                raise AssertionError(f'tool input "{tag}" has no assigned step value')

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
            if self.step.input_register.get(query):
                return True
        return False
    
    def should_assign_default(self, component: CommandComponent) -> bool:
        assert(self.step.tool)
        tag = self.step.tool.tag_manager.get('tool_component', component.get_uuid())
        if not self.register.get(tag):
            return True
        return False
    
    def should_migrate(self, input_value: InputValue) -> bool:
        if input_value.valtype == InputValueType.ENV_VAR:
            return True
        return False
    
    def should_annotate_default(self, tag: str, input_value: InputValue) -> bool:
        component = self.step.get_tool_input(tag)
        if str(component.get_default_value()) == input_value.value:
            return True
        return False







"""

workflow end:

replace all $env_vars with RuntimeValue

detect which connection inputs have not been touched
    - mark each connection input as being linked on the fly
    - write note if any werent linked properly. see unicycler fq1="$fq1"
    - list likely candidates for this value

ask Richard:
- quast fungus="" workflow step

String options should have None instead of "" for step values?
>>> bool("")
False


Tool end:
disallow defaults for File inputs. -> done on the tool parsing end.
- don't want sitations where we have 'in1' default = 'input.fq' or 'fastq' etc


"""

