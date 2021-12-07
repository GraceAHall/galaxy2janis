


from __future__ import annotations
from typing import Optional

from classes.command.Tokens import Token
from galaxy.tools.parameters.basic import DataToolParameter


class Positional:
    def __init__(self, pos: int):
        self.pos = pos
        self.values: set[str] = set()
        self.sources: set[Token] = set()
        self.after_options: bool = False
        self.galaxy_param: Optional[DataToolParameter] = None


    def merge(self, incoming: Positional) -> None:
        # after options
        if incoming.after_options == True:
            self.after_options = True

        # galaxy param reference        
        if incoming.galaxy_param is not None:
            # check the params do not clash
            if self.galaxy_param is not None:
                if not incoming.galaxy_param == self.galaxy_param:
                    raise Exception('two different galaxy params for one component')
            
            self.galaxy_param = incoming.galaxy_param

        # sources
        for token in incoming.sources:
            self.add_token(token)

   
    def add_token(self, the_token: Token) -> None:
        self.values.add(the_token.text)
        self.sources.add(the_token)


    def get_sources(self) -> list[Token]:
        return list(self.sources)


    def get_values(self) -> list[str]:
        return list(self.values)


    def is_optional(self) -> bool:
        return self.token.in_conditional


    def __str__(self) -> str:
        values = ';'.join(self.get_values())
        gx_param_name = self.galaxy_param.name if self.galaxy_param else ''
        return f'{self.pos:<10}{values[:39]:40}{gx_param_name[:19]:20}{self.after_options:>5}'


"""
Flags have a text element and sources
Flags arguments can be included in the command string via sources
Valid sources are RAW_STRING and GX_PARAM 
"""
class Flag:
    def __init__(self, prefix: str):
        self.prefix = prefix
        self.pos: int = 0
        self.sources: set[Token] = set()
        self.galaxy_param: Optional[DataToolParameter] = None

    
    def merge(self, incoming: Positional) -> None:
        # galaxy param reference        
        if incoming.galaxy_param is not None:
            # check the params do not clash
            if self.galaxy_param is not None:
                if not incoming.galaxy_param == self.galaxy_param:
                    raise Exception('two different galaxy params for one component')
            
            self.galaxy_param = incoming.galaxy_param

        # sources
        for token in incoming.sources:
            self.add_token(token)


    def add_token(self, the_token: Token) -> None:
        self.sources.add(the_token)


    def get_sources(self) -> list[Token]:
        return list(self.sources)


    def is_optional(self) -> bool:
        for source in self.sources:
            if not source.in_conditional:
                return False
        return True


    def __str__(self) -> str:
        gx_param_name = self.galaxy_param.name if self.galaxy_param else ''
        return f'{self.pos:<10}{self.prefix[:19]:20}{gx_param_name[:19]:20}'


"""
Options have a flag and an argument 
prefix can be set from a RAW_STRING and/or GX_PARAM?
Sources can be set from just about anything 

sources has a little bit different meaning to as seen in Flags.

"""
class Option:
    def __init__(self, prefix: str, delim: str=' ', splittable: bool=True):
        self.prefix: str = prefix
        self.delim: str = delim
        self.splittable: bool = splittable
        self.pos: int = 0
        self.values: set[str] = set()
        self.sources: set[Token] = set()
        self.galaxy_param: Optional[DataToolParameter] = None


    def merge(self, incoming: Positional) -> None:
        # after options
        if incoming.splittable == False:
            self.splittable = False

        # galaxy param reference        
        if incoming.galaxy_param is not None:
            # check the params do not clash
            if self.galaxy_param is not None:
                if not incoming.galaxy_param == self.galaxy_param:
                    raise Exception('two different galaxy params for one component')
            
            self.galaxy_param = incoming.galaxy_param

        # sources
        for token in incoming.sources:
            self.add_token(token)


    def add_token(self, the_token: Token) -> None:
        self.values.add(the_token.text)
        self.sources.add(the_token)


    def get_values(self) -> list[str]:
        return list(self.values)

    
    def get_sources(self) -> list[Token]:
        return list(self.sources)


    def is_optional(self) -> bool:
        for source in self.sources:
            if not source.in_conditional:
                return False
        return True


    def __str__(self) -> str:
        values = ';'.join(self.get_values())
        gx_param_name = self.galaxy_param.name if self.galaxy_param else ''
        return f'{self.pos:<10}{self.prefix[:19]:20}{values[:39]:40}{gx_param_name[:19]:20}'


class Stdout:
    def __init__(self):
        self.sources: set[Token] = set()
        self.galaxy_param: Optional[DataToolParameter] = None
        #self.datatypes: list[dict[str, str]] = []


    def add_token(self, the_token: Token) -> None:
        self.sources.add(the_token)


    def get_sources(self) -> list[Token]:
        return list(self.sources)


    def __str__(self) -> str:
        the_str = ''

        t = self.sources[0]
        the_str += f'{t.text[:29]:30}{t.gx_ref[:29]:30}{t.type.name:20}{t.in_conditional:>5}'

        if len(self.sources) > 1:
            for t in self.sources[1:]:
                the_str += f'\n{t.text[:29]:30}{t.gx_ref[:29]:30}{t.type.name:20}{t.in_conditional:>5}'

        return the_str