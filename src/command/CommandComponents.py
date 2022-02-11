
# pyright: basic

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from command.Command import Command 
    
from typing import Optional, Union, Any
from collections import Counter

from galaxy.tool_util.parser.output_objects import ToolOutput
from galaxy.tools.parameters.basic import ToolParameter
from command.tokens.Tokens import Token, TokenType

from command.tokens.utils import tokenify



class CommandComponent:
    def __init__(self) -> None:
        self.sources: set[Token] = set()
        self.galaxy_object: Optional[ToolParameter] = None
        self.this_cmdstr_presence: bool = False
        self.presence_array: list[bool] = []

    
    def add_token(self, the_token: Token) -> None:
        self.sources.add(the_token)


    def set_presence(self, presence: bool) -> None:
        self.this_cmdstr_presence = presence


    def update_presence_array(self, cmdstr_count: int) -> None:
        # newly discovered components
        while len(self.presence_array) < cmdstr_count - 1:
            self.presence_array.append(False)

        # now that component is up to date
        self.presence_array.append(self.this_cmdstr_presence)


    def get_token_types(self, as_list: bool=False) -> Union[list[TokenType], set[TokenType]]:
        values = set([t.type for t in self.sources])
        if as_list:
            values = list(values)
        return values
    
    
    def get_token_values(self, as_list: bool=False) -> Union[list[str], set[str]]:
        values = set([t.text for t in self.sources])
        if as_list:
            values = list(values)
        return values


    def get_default_value(self) -> Optional[str]:
        """
        gets the default value for this component.
        if a galaxy object is attached, gets defaut from this source
        else, uses the list of sources (witnessed occurances) to decide 
        what the default should be.
        """
        if self.galaxy_object:
            return self.get_galaxy_default_value()
        return self.get_most_common_token_text()


    def get_galaxy_default_value(self) -> str:
        """
        gets the default value for a galaxy param
        """
        gxobj = self.galaxy_object
        if gxobj:
            if gx_utils.is_tool_parameter(gxobj):
                return gx_utils.get_param_default_value(gxobj)
            elif gx_utils.is_tool_output(gxobj):
                return gx_utils.get_output_default_value(gxobj)

    
    def get_most_common_token_text(self) -> Any:
        """
        gets most commonly occuring text string among source tokens
        prioritises the first witnessed token if equal occurances
        """
        counter = Counter([t.text for t in self.sources])
        max_c = counter.most_common(1)[0][1]
        values = [t.text for t in self.sources if counter[t.text] == max_c]
        return values[0]

    
    def get_galaxy_options(self, as_tokens: bool=False) -> Optional[Union[list[TokenType], list[str]]]:
        if self.galaxy_object and self.galaxy_object.type in ['select', 'boolean']:
            
            opts = gx_utils.get_param_options(self.galaxy_object)
            if as_tokens:
                opts = [tokenify(opt) for opt in opts]
            return opts
        
        return None


    def is_optional(self) -> bool:
        """
        goes through each possible reason why component would be optional
        if no condition is met, returns False
        """
        # positionals aren't optional
        if isinstance(self, Positional):
            return False

        # component doesn't appear in each supplied command string
        if not all(self.presence_array):
            return True
        
        # component appears in each supplied command string, but is always in conditional logic
        if all(self.presence_array):
            if all([t.in_conditional for t in self.sources]):
                return True
        
        # has galaxy object
        gxobj = self.galaxy_object
        if gxobj:
            if gx_utils.is_tool_parameter(gxobj):
                return gx_utils.param_is_optional(gxobj)
            elif gx_utils.is_tool_output(gxobj):
                return gx_utils.output_is_optional(gxobj)              
    
        return False


    def is_array(self) -> bool:
        # has galaxy object
        gxobj = self.galaxy_object
        if gxobj:
            if gx_utils.is_tool_parameter(gxobj):
                return gx_utils.param_is_array(gxobj)
            elif gx_utils.is_tool_output(gxobj):
                return gx_utils.output_is_array(gxobj)    
          
        # NOTE: it may be possible to detect arrays from components without 
        # galaxy objects. Eg strings which can be interpreted as comma-delimited list
        return False



class Positional(CommandComponent):
    def __init__(self, pos: int):
        super().__init__()
        self.pos = pos
        self.is_after_options: bool = False


    def merge(self, incoming: Positional) -> None:
        """
        merges an incoming command component with this component.
        the incoming will be describing the same component (thats why its being merged)
        """
        # after options
        if incoming.is_after_options:
            self.is_after_options = True

        # galaxy param reference        
        if incoming.galaxy_object is not None:
            # check the params do not clash
            if self.galaxy_object is not None:
                if not incoming.galaxy_object == self.galaxy_object:
                    raise Exception('two different galaxy params for one component')
            
            self.galaxy_object = incoming.galaxy_object

        # sources
        for token in incoming.sources:
            self.add_token(token)

    
    def has_unique_value(self) -> bool:
        values = self.get_token_values()
        if len(values) == 1:
            return True
        return False
 

    def __str__(self) -> str:
        values = ';'.join(self.get_token_values())
        has_gx_ref = True if self.galaxy_object is not None else False
        return f'{self.pos:<10}{values[:39]:40}{has_gx_ref:10}{self.is_after_options:>5}'



class Flag(CommandComponent):
    def __init__(self, prefix: str):
        super().__init__()
        self.prefix = prefix
        self.pos: int = 0


    def merge(self, incoming: Flag) -> None:
        """
        merges an incoming command component with this component.
        the incoming will be describing the same component (thats why its being merged)
        """
        # galaxy param reference        
        if incoming.galaxy_object is not None:
            # check the params do not clash
            if self.galaxy_object is not None:
                if not incoming.galaxy_object == self.galaxy_object:
                    raise Exception('two different galaxy params for one component')
            
            self.galaxy_object = incoming.galaxy_object
            print()

        # sources
        for token in incoming.sources:
            self.add_token(token)


    def __str__(self) -> str:
        has_gx_ref = True if self.galaxy_object is not None else False
        return f'{self.pos:<10}{self.prefix[:19]:20}{has_gx_ref:10}'



class Option(CommandComponent):
    def __init__(self, prefix: str, delim: str=' ', splittable: bool=True):
        super().__init__()
        self.prefix: str = prefix
        self.delim: str = delim
        self.splittable: bool = splittable
        self.pos: int = 0


    def merge(self, incoming: Option) -> None:
        """
        merges an incoming command component with this component.
        the incoming will be describing the same component (thats why its being merged)
        """
        # after options
        if not incoming.splittable:
            self.splittable = False

        # galaxy param reference        
        if incoming.galaxy_object is not None:
            # check the params do not clash
            if self.galaxy_object is not None:
                if not incoming.galaxy_object == self.galaxy_object:
                    raise Exception('two different galaxy params for one component')
            
            self.galaxy_object = incoming.galaxy_object

        # sources
        for token in incoming.sources:
            self.add_token(token)


    def __str__(self) -> str:
        values = ';'.join(self.get_token_values())
        has_gx_ref = True if self.galaxy_object is not None else False
        return f'{self.pos:<10}{self.prefix[:19]:20}{values[:39]:40}{has_gx_ref:10}'



class Output:
    def __init__(self, gx_output: ToolOutput):
        self.galaxy_object = gx_output
        self.is_stdout: bool = False
        self.selector: str = self.get_selector()


    def set_stdout(self) -> None:
        self.is_stdout = True


    def is_optional(self) -> bool:
        # NOTE - janis does not allow optional outputs
        return False


    def is_array(self) -> bool:
        gxobj = self.galaxy_object
        if gxobj.output_type == 'collection':
            return True

        elif gxobj.output_type == 'data' and len(gxobj.output_discover_patterns) > 0:
            return True
        
        return False


    def get_name(self) -> str:
        return self.galaxy_object.name

      
    def get_selector(self) -> str:
        """gets the selector type for janis output detection"""
        if hasattr(self, 'selector'):
            return self.selector

        if self.galaxy_object:
            return gx_utils.get_output_selector(self.galaxy_object)
        
      
    def get_selector_contents(self, command: Command) -> str:
        selector = self.get_selector()
        if selector == 'WildcardSelector':
            return gx_utils.get_output_files_path(self.galaxy_object)
        
        elif selector == 'InputSelector':
            components = command.get_components_possessing_gxobj(self.galaxy_object.name, valid_types=[Positional, Option])
            assert len(components) == 1
            return components[0].get_name()
             
    
    def __str__(self) -> str:
        out_str = ''
        return out_str
