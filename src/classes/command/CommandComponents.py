
# pyright: strict

from __future__ import annotations
from typing import Optional, Union, Any
from collections import Counter

from classes.command.Tokens import Token, TokenType
from galaxy.tools.parameters.basic import ToolParameter


class CommandComponent:
    def __init__(self) -> None:
        self.sources: set[Token] = set()
        self.galaxy_object: Optional[ToolParameter] = None

    
    def add_token(self, the_token: Token) -> None:
        self.sources.add(the_token)


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


    def get_default(self) -> Any:
        """
        gets the default value for this component.
        if a galaxy object it attached, gets defaut from this source
        else, uses the list of sources (witnessed occurances) to decide 
        what the default should be.
        """
        if self.galaxy_object is not None:
            return self.get_galaxy_default()
        return self.get_primary_value()


    def get_galaxy_default(self) -> Any:
        if self.galaxy_object.type in ['data', 'data_collection']:
            # use static options
            pass
        elif self.galaxy_object.type == 'select':
            pass
        else:
            # TODO HERE 
            return ''


    def get_main_select_option(self)


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
        if type(self) == Positional:
            return False

        for source in self.sources:
            if not source.in_conditional:
                return False

        return True



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