
import ast 
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

from galaxy2janis.gx.command.components import OutputComponent
from galaxy2janis.gx.command.components import InputComponent

from galaxy2janis import tags
from galaxy2janis import expressions


@dataclass
class InputValue(ABC):
    component: Optional[InputComponent]

    def __post_init__(self):
        self.scatter: bool = False

    @property
    def comptype(self) -> Optional[str]:
        return type(self.component).__name__.lower() 

    @property
    def input_tag(self) -> str:
        """get the str tag for this tool input"""
        if self.component:
            return self.component.tag
        else:
            return 'UNKNOWN'
    
    @property
    @abstractmethod
    def wrapped_value(self) -> str:
        """
        get the str value for this tool input.
        for workflow inputs & connections, returns janis style
        workflow object name references.
        """
        ...


def get_comptype(component: InputComponent | OutputComponent) -> str:
    return type(component).__name__.lower() 

def infer_value_type(component: Optional[InputComponent], value: Any) -> str:
    """
    only StaticValueLinkingStrategy and DefaultValueLinkingStrategy 
    call select_input_value_type(). don't need to worry about CONNECTION and RUNTIME_VALUE
    """
    if is_bool(value):
        return 'boolean'
    elif is_numeric(component, value):
        return 'numeric'
    elif is_none(value):
        return 'none'
    elif expressions.is_var(value) or expressions.has_var(value):
        return 'env_var'
    else:
        return 'string'

def is_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return True
    return False

def is_none(value: Any) -> bool:
    if value is None:
        return True
    return False

def is_numeric(component: Optional[InputComponent | OutputComponent], value: Any) -> bool:
    """does information from the supplied component and/or value suggest a numeric datatype"""
    if expressions.is_int(str(value)) or expressions.is_float(str(value)):
        return True
    elif component and _has_numeric_datatype(component):
        return True
    return False

def _has_numeric_datatype(component: InputComponent | OutputComponent) -> bool:
    jtype = component.datatype
    numeric_classes = ['Int', 'Float']
    if jtype.classname in numeric_classes:
        return True
    return False
    

@dataclass
class StaticInputValue(InputValue):
    string_value: str
    default: bool

    def __post_init__(self):
        self.scatter: bool = False
    
    @property
    def is_none(self) -> bool:
        if infer_value_type(self.component, self.string_value) == 'none':
            return True
        return False
    
    @property
    def raw_value(self) -> Any:
        """
        get the typed value for this InputValue.
        literal_eval will take care of most cases.
        that said, sometimes it doesn't work for values which could be 
        interpreted as strings OR numeric types.

        eg self.string_value == '7', it will return as str('7'). 
        we may know this should actually be an int given other data. 
        """
        # None, True / False, string will be taken care of here.
        # try: except needed because literal_eval() will fail on specific strings
        val = self.string_value

        # empty string
        if val == '':       
            return None
        
        # list, tuple, dict
        for open_b, close_b in [('(', ')'), ('[', ']'), ('{', '}')]:
            if val[0] == open_b and val[-1] == close_b:
                val = ast.literal_eval(val)
        
        if val in ['True', 'False', 'None']:
            val = ast.literal_eval(val)
        
        # cast str to int or float if appropriate.
        if isinstance(val, str):
            if is_numeric(self.component, val):
                if val.isdecimal():
                    val = int(val)     # integer 
                else:
                    val = float(val)   # not an integer, so must be float
        return val

    @property
    def wrapped_value(self) -> str:
        if self._should_wrap_value():
            return f'"{self.raw_value}"'
        else:
            return f'{self.raw_value}'
        
    def _should_wrap_value(self) -> bool:
        if infer_value_type(self.component, self.string_value) == 'string':
            return True
        if infer_value_type(self.component, self.string_value) == 'env_var':
            return True
        return False



@dataclass
class ConnectionInputValue(InputValue):
    step_uuid: str
    out_uuid: str
    
    @property
    def wrapped_value(self) -> str:
        step_tag = tags.get(self.step_uuid)
        out_tag = tags.get(self.out_uuid)
        return f'w.{step_tag}.{out_tag}'
    

@dataclass
class WorkflowInputInputValue(InputValue):
    input_uuid: str
    is_runtime: bool

    @property
    def wrapped_value(self) -> str:
        wflow_inp_tag = tags.get(self.input_uuid)
        return f'w.{wflow_inp_tag}'

