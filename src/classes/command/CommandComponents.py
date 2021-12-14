
# pyright: basic

from __future__ import annotations
from typing import Optional, Union, Any
from collections import Counter

from classes.command.Tokens import Token, TokenType
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
            if self.galaxy_object.optional == True:
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
            elif g_obj.type == 'data' and g_obj.multiple == True:
                return True
        
        # NOTE: it may be possible to detect arrays from components without 
        # galaxy objects. Eg strings which can be interpreted as comma-delimited list
        return False



class Positional(CommandComponent):
    def __init__(self, pos: int):
        super().__init__()
        self.pos = pos
        self.after_options: bool = False


    def merge(self, incoming: Positional) -> None:
        # after options
        if incoming.after_options == True:
            self.after_options = True

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
        return f'{self.pos:<10}{values[:39]:40}{has_gx_ref:10}{self.after_options:>5}'




class Flag(CommandComponent):
    def __init__(self, prefix: str):
        super().__init__()
        self.prefix = prefix
        self.pos: int = 0


    def merge(self, incoming: Flag) -> None:
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
        # after options
        if incoming.splittable == False:
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



class Stdout(CommandComponent):
    def __init__(self):
        super().__init__()
  
    
    def __str__(self) -> str:
        the_str = ''

        t = self.sources[0]
        the_str += f'{t.text[:29]:30}{t.gx_ref[:29]:30}{t.type.name:20}{t.in_conditional:>5}'

        if len(self.sources) > 1:
            for t in self.sources[1:]:
                the_str += f'\n{t.text[:29]:30}{t.gx_ref[:29]:30}{t.type.name:20}{t.in_conditional:>5}'

        return the_str