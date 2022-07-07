

from abc import ABC, abstractmethod
from typing import Optional
from shellparser.components.CommandComponent import CommandComponent
from shellparser.components.inputs.Flag import Flag
from shellparser.components.inputs.Option import Option
from shellparser.components.inputs.Positional import Positional
from entities.workflow import WorkflowStep

from entities.workflow import ConnectionInputValue, DefaultInputValue, InputValue, InputValueType, StaticInputValue, WorkflowInputInputValue
from entities.workflow import Workflow
from datatypes.core import DEFAULT_DATATYPE


class ToolInputLine(ABC):
    def __init__(self, invalue: InputValue, step: WorkflowStep, workflow: Workflow):
        self.invalue = invalue
        self.step = step
        self.workflow = workflow

    @property
    @abstractmethod
    def tag_and_value(self) -> str:
        ...

    @property
    @abstractmethod
    def special_label(self) -> Optional[str]:
        ...
    
    @property
    @abstractmethod
    def argument(self) -> Optional[str]:
        ...
    
    @property
    @abstractmethod
    def datatype(self) -> str:
        ...
    
    @property
    def default(self) -> bool:
        if self.invalue.is_default:
            return True
        return False

    def value_as_text(self) -> str:


    def wrap(self, text: str) -> str:
        if self.should_quote():
            return f'"{text}"'
        return text

    def should_quote(self) -> bool:
        if isinstance(self.invalue, StaticInputValue) or isinstance(self.invalue, DefaultInputValue):
            quoted_types = [InputValueType.STRING, InputValueType.RUNTIME]
            if self.invalue.valtype in quoted_types:
                return True
        return False


class LinkedInputLine(ToolInputLine):
    def __init__(self, invalue: InputValue, component: CommandComponent, step: WorkflowStep, workflow: Workflow):
        super().__init__(invalue, step, workflow)
        self.component = component
 
    @property
    def tag_and_value(self) -> str:
        tag = self.step.tool.tag_manager.get(self.component.uuid) # type: ignore
        value = self.value_as_text()
        return f'{tag}={value},'
    
    @property
    def special_label(self) -> Optional[str]:
        match self.invalue:
            case ConnectionInputValue():
                return 'INPUT CONNECTION'
            case WorkflowInputInputValue():
                if self.invalue.is_runtime:
                    return 'RUNTIME VALUE'
            case _:
                pass
        return None
    
    @property
    def argument(self) -> Optional[str]:
        if isinstance(self.component, Positional):
            return 'positional'
        elif isinstance(self.component, Flag) or isinstance(self.component, Option):
            return self.component.prefix
        raise RuntimeError()
    
    @property
    def datatype(self) -> str:
        return self.component.janis_datatypes[0].classname
        


class UnlinkedInputLine(ToolInputLine):

    @property
    def tag_and_value(self) -> str:
        value = self.value_as_text()
        return f'#UNKNOWN={value},'
    
    @property
    def special_label(self) -> Optional[str]:
        return f"UNLINKED INPUT ({self.invalue.abstract_value})"
       
    @property
    def argument(self) -> Optional[str]:
        return None
    
    @property
    def datatype(self) -> str:
        match self.invalue:
            case WorkflowInputInputValue():
                winp = self.workflow.get_input(input_uuid=self.invalue.input_uuid)
                assert(winp)
                return winp.janis_datatypes[0].classname
            case ConnectionInputValue():
                step = self.workflow.steps[self.invalue.step_id]
                toolout = step.outputs.get(self.invalue.step_output).tool_output
                assert(toolout)
                return toolout.janis_datatypes[0].classname
            case StaticInputValue():
                if self.invalue.gxparam:
                    pass
            case _:
                pass
        return DEFAULT_DATATYPE.classname
    


