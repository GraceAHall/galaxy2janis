

from entities.workflow.step.tool_values import InputValue
from shellparser.components.inputs.InputComponent import InputComponent

from .ValueLinker import ValueLinker
from ..utils import create_workflow_input
from ..factory import main as factory

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
                # 'component' is the tool component we are getting a value for.
                # as 'is_directly_linkable' was true, we know the galaxy step provided a value.
                # the value may be an input connection, runtime value (user set) or static value. 
                value = self.create_input_value(component)
                register.update_linked(component.uuid, value)

    def create_input_value(self, component: InputComponent) -> InputValue:
        """
        create an InputValue for this tool component using supplied step input values.
        we know that the component has a galaxy param, and that the same galaxy param
        has a supplied value (or connection or runtime value specified) in the step input values. 
        this function grabs that supplied value, then creates a formalised InputValue. 
        it also does other necessary functions - in the case of a galaxy 'runtime value', 
        this needs to become a WorkflowInput in janis world. a WorkflowInput would be created, 
        added to the Workflow, and also added to the InputValue (WorkflowInputInputValue). 
        this says 'for step x using tool y, the tool input component z gets its value from 
        our new WorkflowInput'
        """
        inputs = self.step.inputs
        step_input = inputs.get(component.gxparam.name)  # type: ignore
        assert(step_input)
        match step_input:
            case StaticStepInput():
                value = step_input.value
                is_default = True if component.default_value == value else False
                invalue = factory.static(component, value=value, default=is_default)
            case ConnectionStepInput():
                self.workflow.get_step(step_input.step_uuid)
                invalue = factory.connection()
            case WorkflowInputStepInput():
                winp = create_workflow_input(component) # create new WorkflowInput
                self.workflow.add_input(winp)  # register it in the Workflow
                invalue = factory.workflow_input(component, winp=winp) # create the InputValue
            case RuntimeStepInput():
                winp = create_workflow_input(component)
                self.workflow.add_input(winp)
                invalue = factory.workflow_input(component, winp=winp, is_runtime=True)
            case _:
                raise RuntimeError()
        return invalue
    
    def is_directly_linkable(self, component: InputComponent) -> bool:
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
    

