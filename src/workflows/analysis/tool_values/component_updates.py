



from entities.tool.Tool import Tool

from shellparser.components.CommandComponent import CommandComponent
from shellparser.components.inputs.Option import Option
from shellparser.components.inputs.Positional import Positional
from entities.workflow.step.step import WorkflowStep


from entities.workflow.step.tool_values import (
    InputValue, 
    StaticInputValue, 
    InputValueType, 
    DefaultInputValue,
    InputValueRegister 
)

"""
updates understanding of tool inputs using the values assigned to each input.
example: a tool input was marked not optional, but it does not appear in the partially evaluated
cheetah text. since it doesn't appear, it must be optional. 
"""

def update_component_knowledge(step: WorkflowStep):
    updater = ToolInputUpdater(step.tool, step.tool_values)
    updater.update()

# TODO this is bad  
class ToolInputUpdater:
    def __init__(self, tool: Tool, valregister: InputValueRegister):
        self.tool = tool
        self.valregister = valregister

    def update(self) -> None:
        self.update_components_via_value()
        #self.update_components_via_presence()

    def update_components_via_value(self) -> None:
        for uuid, value in self.valregister.linked:
            component = self.tool.get_input(uuid)
            self.update_component_from_workflow_value(component, value)
    
    def update_components_via_presence(self) -> None:
        """
        if component is not optional, but has default=None and no reference in StepInputs,
        mark this as optional as its not referred to anywhere. must be optional
        """
        for component in self.tool.list_inputs():
            comp_uuid = component.uuid
            if not component.optional:
                value = self.valregister.get(comp_uuid)
                if isinstance(value, DefaultInputValue) and value.valtype == InputValueType.NONE:
                    self.update_component_optionality(component)

    def update_component_from_workflow_value(self, component: CommandComponent, input_value: InputValue) -> None:
        # optionality
        # datatypes? only in rare cases
        match input_value:
            case StaticInputValue(is_default_value=True):  # default means we couldn't link
                self.update_component_optionality(component)
            case StaticInputValue(valtype=InputValueType.NONE): # specifically assigned None
                self.update_component_optionality(component)
            case StaticInputValue(valtype=InputValueType.ENV_VAR): # ?? don't do anything
                pass
            case _:
                pass

    def update_component_optionality(self, component: CommandComponent) -> None:
        if isinstance(component, Option) or isinstance(component, Positional):
            component.forced_optionality = True

    def update_component_datatypes(self, component: CommandComponent, input_value: InputValue) -> None:
        raise NotImplementedError()
