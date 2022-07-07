

from abc import ABC, abstractmethod

from entities.workflow import Workflow
from entities.workflow import WorkflowStep
from shellparser.components.inputs.InputComponent import InputComponent


class ValueLinker(ABC):
    """
    assigns values to each tool argument given some reference information
    
    InputDictValueLinker looks up values directly from the step input dict
    when possible (a gxparam is attached to the component)

    CheetahValueLinker follows similar logic to InputDictValueLinker, except also 
    templates the <command> with the step input dict, then uses the templated <command> 
    to locate arguments and pull their value
    """
    def __init__(self, step: WorkflowStep, workflow: Workflow):
        self.step = step
        self.workflow = workflow

    @abstractmethod
    def link(self) -> None:
        """links tool arguments to their value for a given workflow step"""
        ...

    def get_linkable_components(self) -> list[InputComponent]:
        out: list[InputComponent] = []
        # return tool components which don't yet appear in register
        register = self.step.tool_values
        components = self.step.tool.list_inputs()
        #components = self.step.tool.list_inputs() # this could be subworkflow inputs
        for component in components:
            if not register.get(component.uuid):
                out.append(component)
        return out
