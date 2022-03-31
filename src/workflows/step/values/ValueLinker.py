



from command.components.CommandComponent import CommandComponent
from workflows.step.Step import ToolStep
from workflows.step.values.InputValue import InputValueType
from workflows.step.values.InputValueFactory import InputValueFactory
from workflows.step.values.InputValueRegister import InputValueRegister
from workflows.workflow.Workflow import Workflow


# module entry
def link_step_values(workflow: Workflow):
    for step in workflow.steps.values():
        assert(step.tool)
        step.input_register.assign_gxparams(step.tool)  # assigns actual Param objects to gxparam field of inputs
        linker = ValueLinker(step, workflow)
        linker.link()


class ValueLinker:
    def __init__(self, step: ToolStep, workflow: Workflow):
        self.step = step
        self.workflow = workflow
        self.values: InputValueRegister = InputValueRegister()
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

    def assign_supplied_values(self) -> None:
        # link tool components to static and connection inputs
        assert(self.step.tool)
        for component in self.step.tool.get_inputs():
            if self.is_directly_linkable(component):
                self.assign_value(component)

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

    def assign_value(self, component: CommandComponent) -> None:
        tag = component.get_janis_tag()
        query = component.gxparam.name 
        step_input = self.step.input_register.get(query)
        assert(step_input)
        value = self.factory.create(component, step_input, self.workflow)
        self.values.update(tag, value)

    # NOTE - EVERYTHING BELOW HERE IS WAYYY TOO NESTED
    def update_linked_component_knowledge(self) -> None:
        # CHECK
        pass

    def assign_default_values(self) -> None:
        assert(self.step.tool)
        for component in self.step.tool.get_inputs():
            tag = component.get_janis_tag()
            if not self.values.get(tag):
                value = self.factory.create_default(component)
                self.values.update(tag, value)

    def migrate_defaults_to_runtime(self) -> None:
        assert(self.step.tool)
        for tag, input_value in self.values.list_values():
            component = self.step.tool.get_input(tag)
            if component:
                if input_value.valtype == InputValueType.ENV_VAR:
                    new_value = self.factory.create_runtime(component)
                    self.values.update(tag, new_value)
    
    def annotate_supplied_values_as_default(self) -> None:
        # CHECK
        assert(self.step.tool)
        for tag, input_value in self.values.list_values():
            component = self.step.tool.get_input(tag)
            if component:
                if str(component.get_default_value()) == input_value.value:
                    input_value.is_default_value = True
    
    def assign_unlinked_connections(self) -> None:
        input_register = self.step.input_register
        value_register = self.step.values
        for step_input in input_register.list_inputs():
            if not step_input.linked:
                value_register.update_unlinked(step_input)

    def assert_all_components_assigned(self) -> None:
        # CHECK
        assert(self.step.tool) # TODO remove this annoying shit
        for component in self.step.tool.get_inputs():
            tag = component.get_janis_tag()
            if not self.values.get(tag):
                raise AssertionError(f'tool input "{tag}" has no assigned step value')






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

