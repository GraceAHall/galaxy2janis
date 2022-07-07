

from entities.workflow.step.tool_values import InputValue
from shellparser.components.CommandComponent import CommandComponent

from .ValueLinker import ValueLinker
from factory import main as factory

from entities.workflow.step.inputs import (
    WorkflowInputStepInput,
    ConnectionStepInput,
    StaticStepInput,
    RuntimeStepInput
)


class StepInputsLinker(ValueLinker):

    def link(self) -> None:
        # link tool components to static and connection inputs
        register = self.step.tool_values
        
        for component in self.get_linkable_components():
            if self.is_directly_linkable(component):
                value = self.create_input_value(component)
                register.update_linked(component.uuid, value)

    def create_input_value(self, component: CommandComponent) -> InputValue:
        inputs = self.step.inputs
        step_input = inputs.get(component.gxparam.name)  # type: ignore
        assert(step_input)
        match step_input:
            case StaticStepInput():
                value = factory.static()
            case ConnectionStepInput():
                value = factory.connection()
            case WorkflowInputStepInput():
                value = factory.workflow_input(component, )
            case RuntimeStepInput():
                value = factory.workflow_input(component, is_runtime=True)
            case _:
                raise RuntimeError()
        return value
    
    def is_directly_linkable(self, component: CommandComponent) -> bool:
        """
        checks whether a janis tool input can actually be linked to a value in the 
        galaxy workflow step.
        only possible if the component has a gxparam, and that gxparam is referenced as a
        ConnectionStepInput, RuntimeStepInput or StaticStepInput
        """
        inputs = self.step.inputs
        if component.gxparam:
            query = component.gxparam.name 
            if inputs.get(query):
                return True
        return False
    

