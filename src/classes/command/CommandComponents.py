
# pyright: basic

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from classes.command.Command import Command 
    
from typing import Optional, Union, Any
from collections import Counter
import regex as re

from classes.command.Tokens import Token, TokenType
from galaxy.tool_util.parser.output_objects import ToolOutput
from galaxy.tools.parameters.basic import ToolParameter

from utils.token_utils import tokenify


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
    
    
    def get_values(self, as_list: bool=False) -> Union[list[str], set[str]]:
        values = set([t.text for t in self.sources])
        if as_list:
            values = list(values)
        return values


    def get_default(self) -> Optional[str]:
        """
        gets the default value for this component.
        if a galaxy object is attached, gets defaut from this source
        else, uses the list of sources (witnessed occurances) to decide 
        what the default should be.
        """
        if self.galaxy_object is not None:
            return self.get_galaxy_default()
        return self.get_primary_value()


    def get_galaxy_default(self) -> Optional[str]:
        """
        gets the default value for a galaxy param
        """
        if self.galaxy_object is not None:
            if self.galaxy_object.type == 'select':
                return self.get_galaxy_primary_option()

            elif self.galaxy_object.type not in ['data', 'data_collection']:
                if self.galaxy_object.value is not None:
                    return self.galaxy_object.value

        return None


    def get_galaxy_primary_option(self) -> Optional[str]:
        if self.galaxy_object is not None and self.galaxy_object.type == 'select':
            for opt in self.galaxy_object.static_options:
                if opt[2] == True:
                    return opt[1]
            
            return self.galaxy_object.static_options[0][1]
        
        return None
    
    
    def get_galaxy_options(self, as_tokens: bool=False) -> Union[list[TokenType], list[str]]:
        opts = []
        if self.galaxy_object is not None and self.galaxy_object.type == 'select':
            opts = self.galaxy_object.legal_values
            
        if as_tokens:
            opts = [tokenify(opt) for opt in opts]
        
        return opts


    def get_primary_value(self) -> Any:
        """
        gets most commonly occuring text string among source tokens
        prioritises the first witnessed token if equal occurances
        """
        counter = Counter([t.text for t in self.sources])
        max_c = counter.most_common(1)[0][1]
        values = [t.text for t in self.sources if counter[t.text] == max_c]
        return values[0]


    def is_optional(self) -> bool:
        """
        goes through each possible reason why component would be optional
        if no condition is met, returns False
        """
        # positionals aren't optional
        if type(self) == Positional:
            return False

        # has galaxy object
        if self.galaxy_object is not None:
            # optionality explicitly set as true in galaxy object
            if self.galaxy_object.optional:
                return True
            # galaxy values include a blank string
            if '' in self.get_galaxy_values():
                return True
        
        # component doesn't appear in each supplied command string
        if not all(self.presence_array):
            return True
        
        # component appears in each supplied command string, but is always in conditional logic
        if all(self.presence_array):
            if all([t.in_conditional for t in self.sources]):
                return True

        return False


    def get_galaxy_values(self) -> list[str]:
        if self.galaxy_object is not None:
            if self.galaxy_object.type in ['select', 'boolean']:
                return self.galaxy_object.legal_values
            elif self.galaxy_object.type not in ['data', 'data_collection']:
                if self.galaxy_object.value is not None:
                    return [self.galaxy_object.value]
        
        return []


    def is_array(self) -> bool:
        # defined in galaxy object
        g_obj = self.galaxy_object
        if g_obj is not None:
            if g_obj.type == 'data_collection':
                return True
            elif g_obj.type == 'data' and g_obj.multiple:
                return True
        
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
        values = self.get_values()
        if len(values) == 1:
            return True
        return False
 

    def __str__(self) -> str:
        values = ';'.join(self.get_values())
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
        values = ';'.join(self.get_values())
        has_gx_ref = True if self.galaxy_object is not None else False
        return f'{self.pos:<10}{self.prefix[:19]:20}{values[:39]:40}{has_gx_ref:10}'



class Output:
    def __init__(self, gx_output: ToolOutput):
        self.galaxy_object = gx_output
        self.is_stdout: bool = False
        self.selector: str = self.get_selector()

        """
        SELECTOR
        pass        

        SELECTOR CONTENTS
        data|collection.discover_datasets.pattern
        data|collection.discover_datasets.directory
        data|collection.discover_datasets.match_relative_path
        
        """

    def set_stdout(self) -> None:
        self.is_stdout = True


    def is_array(self) -> bool:
        gxobj = self.galaxy_object
        if gxobj.output_type == 'collection':
            return True

        elif gxobj.output_type == 'data' and len(gxobj.output_discover_patterns) != 0:
            return True
        
        return False


    def is_optional(self) -> bool:
        # NOTE - janis does not allow optional outputs
        return False


    def get_name(self) -> str:
        return self.galaxy_object.name

      
    def get_selector(self) -> str:
        """gets the selector type for janis output detection"""
        if hasattr(self, 'selector'):
            return self.selector
        elif self.is_wildcard_selector():
            return 'WildcardSelector'
        return 'InputSelector'
        

    def is_wildcard_selector(self) -> bool:
        gobj = self.galaxy_object
        
        # data output
        if gobj.output_type == 'data':
            if gobj.from_work_dir is not None:
                return True
        
            elif len(gobj.output_discover_patterns) != 0:
                return True
        
        # collection output
        elif gobj.output_type == 'collection':
            return True
            # NOTE - add support for the following later:
            # defined output elems in collection
            # structured_like=""

        return False


    def get_selector_contents(self, command: Command) -> str:
        if self.selector == 'WildcardSelector':
            self.get_files_path()
        
        elif self.selector == 'InputSelector':
            component = command.get_component_with_gxout_reference(self.galaxy_object.name)
            

        # weird fallback
        return ''



    def transform_pattern(self, pattern: str) -> str:
        transformer = {
            '__designation__': '*',
            '.*?': '*',
            '\\.': '.',
        }

        # # remove anything in brackets
        # pattern_list = pattern.split('(?P<designation>')
        # if len(pattern_list) == 2:
        #     pattern_list[1] = pattern_list[1].split(')', 1)[-1]

        # find anything in between brackets
        bracket_strings = re.findall("\\((.*?)\\)", pattern)

        # remove brackets & anything previously found (lazy)
        pattern = pattern.replace('(', '').replace(')', '')
        for the_string in bracket_strings:
            if '<ext>' in the_string:
                pattern = pattern.replace(the_string, '') # lazy and bad
            pattern = pattern.replace(the_string, '*')

        for key, val in transformer.items():
            pattern = pattern.replace(key, val)

        # remove regex start and end patterns
        pattern = pattern.rstrip('$').lstrip('^')
        return pattern


    def update_output_selector_from_command(self) -> None:
        command = self.tool.command

        # is this a TODO? add logic incase of positional output? 
        # would be pretty weird 
        for positional in command.get_positionals():
            pass
        
        for option in command.get_options():
            for source in option.sources:
                if source.type == TokenType.GX_OUT:
                    if '$' + output.gx_var == source.gx_ref:
                        output.selector = 'InputSelector'
                        output.selector_contents = option.prefix.lstrip('-')

    
  
    
    def __str__(self) -> str:
        out_str = ''
        return out_str