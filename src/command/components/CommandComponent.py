

from __future__ import annotations
from typing import Any, Optional, Protocol

from tool.param.Param import Param


class CommandComponent(Protocol):
    gxvar: Optional[Param]
    presence_array: list[bool]
    cmd_pos: int
    
    def update(self, incoming: CommandComponent, cmdstr_index: int):
        """
        updates this component with information from another similar component. 
        also sets the component as being present in the cmdstr being parsed.
        example: 
        str1: abricate $input.fastq --db card > out.txt
        str2: abricate $input.fastq --db resfinder > out.txt
        the --db option should be updated so we know its possible values
        are (at least) card, resfinder
        """
        ...

    def update_presence_array(self, cmdstr_index: int, fill_false: bool=False):
        """
        sets the presence of the component in the current cmdstr being parsed.
        """
        ...
    
    def get_default_value(self) -> Any:
        """
        gets the default value of the component.
        uses the components observed values (positionals / options) and
        galaxy param information if available.
        """
        ...
    
    def is_optional(self) -> bool:
        """
        returns whether the component is optional or not.
        uses galaxy param information if available, otherwise uses the presence array. flags are always optional
        """
        ...

    def is_array(self) -> bool:
        """
        returns whether the component is an array or not
        uses galaxy param information if available.
        flags components are never arrays.
        """
        ...

    


"""


def get_token_types_old(as_list: bool=False) -> Union[list[TokenType], set[TokenType]]:
    values = set([t.type for t in self.sources])
    if as_list:
        values = list(values)
    return values


def get_token_values_old(as_list: bool=False) -> Union[list[str], set[str]]:
    values = set([t.text for t in self.sources])
    if as_list:
        values = list(values)
    return values


def get_default_value_old() -> Optional[str]:
    
    # gets the default value for this component.
    # if a galaxy object is attached, gets defaut from this source
    # else, uses the list of sources (witnessed occurances) to decide 
    # what the default should be.
    
    if self.gxvar:
        return self.get_galaxy_default_value()
    return self.get_most_common_token_text()


def get_galaxy_default_value() -> str:
    
    # gets the default value for a galaxy param
    
    gxobj = self.gxvar
    if gxobj:
        if gx_utils.is_tool_parameter(gxobj):
            return gx_utils.get_param_default_value(gxobj)
        elif gx_utils.is_tool_output(gxobj):
            return gx_utils.get_output_default_value(gxobj)


def get_most_common_token_text() -> Any:
    
    # gets most commonly occuring text string among source tokens
    # prioritises the first witnessed token if equal occurances
    
    counter = Counter([t.text for t in self.sources])
    max_c = counter.most_common(1)[0][1]
    values = [t.text for t in self.sources if counter[t.text] == max_c]
    return values[0]


def get_galaxy_options(as_tokens: bool=False) -> Optional[Union[list[TokenType], list[str]]]:
    if self.gxvar and self.gxvar.type in ['select', 'boolean']:
        
        opts = gx_utils.get_param_options(self.gxvar)
        if as_tokens:
            opts = [tokenify(opt) for opt in opts]
        return opts
    
    return None


def is_optional() -> bool:
    
    # goes through each possible reason why component would be optional
    # if no condition is met, returns False
    
    # positionals aren't optional
    if isinstance(Positional):
        return False

    # component doesn't appear in each supplied command string
    if not all(self.presence_array):
        return True
    
    # component appears in each supplied command string, but is always in conditional logic
    if all(self.presence_array):
        if all([t.in_conditional for t in self.sources]):
            return True
    
    # has galaxy object
    gxobj = self.gxvar
    if gxobj:
        if gx_utils.is_tool_parameter(gxobj):
            return gx_utils.param_is_optional(gxobj)
        elif gx_utils.is_tool_output(gxobj):
            return gx_utils.output_is_optional(gxobj)              

    return False


def is_array() -> bool:
    # has galaxy object
    gxobj = self.gxvar
    if gxobj:
        if gx_utils.is_tool_parameter(gxobj):
            return gx_utils.param_is_array(gxobj)
        elif gx_utils.is_tool_output(gxobj):
            return gx_utils.output_is_array(gxobj)    
        
    # NOTE: it may be possible to detect arrays from components without 
    # galaxy objects. Eg strings which can be interpreted as comma-delimited list
    return False

"""