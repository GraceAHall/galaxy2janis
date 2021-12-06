

from classes.command.Tokens import Token



class Positional:
    def __init__(self, pos: int, token: Token, after_options: bool):
        self.pos = pos
        self.token = token
        self.after_options = after_options
        self.datatypes: list[dict[str, str]] = []


    def is_optional(self) -> bool:
        return self.token.in_conditional


    def __str__(self) -> str:
        t = self.token
        return f'{self.pos:<10}{t.text[:19]:20}{t.gx_ref[:19]:20}{t.type.name:20}{self.after_options:>5}'


"""
Flags have a text element and sources
Flags arguments can be included in the command string via sources
Valid sources are RAW_STRING and GX_PARAM 
"""
class Flag:
    def __init__(self, prefix: str):
        self.prefix: str = prefix
        self.pos: int = 0
        self.sources: list[Token] = [] 
        self.datatypes: list[dict[str, str]] = []


    def is_optional(self) -> bool:
        for source in self.sources:
            if not source.in_conditional:
                return False
        return True


    def __str__(self) -> str:
        """
        print(f'{"prefix":30}{"token type":>20}')
        """
        
        the_str = ''

        t = self.sources[0]
        the_str += f'{t.text[:29]:30}{t.gx_ref[:29]:30}{t.type.name:20}{t.in_conditional:>5}'

        if len(self.sources) > 1:
            for t in self.sources[1:]:
                the_str += f'\n{t.text[:29]:30}{t.gx_ref[:29]:30}{t.type.name:20}{t.in_conditional:>5}'

        return the_str


"""
Options have a flag and an argument 
prefix can be set from a RAW_STRING and/or GX_PARAM?
Sources can be set from just about anything 

sources has a little bit different meaning to as seen in Flags.

"""
class Option:
    def __init__(self, prefix: str, delim: str=' '):
        self.prefix: str = prefix
        self.delim: str = delim
        self.pos: int = 0
        self.sources: list[Token] = []
        self.datatypes: list[dict[str, str]] = []


    def is_optional(self) -> bool:
        for source in self.sources:
            if not source.in_conditional:
                return False
        return True


    def __str__(self) -> str:
        the_str = ''

        t = self.sources[0]
        the_str += f'{self.prefix[:29]:30}{t.text[:29]:30}{t.gx_ref[:29]:30}{t.type.name:20}{t.in_conditional:>5}'

        if len(self.sources) > 1:
            for t in self.sources[1:]:
                the_str += f'\n{"":30}{t.text[:29]:30}{t.gx_ref[:29]:30}{t.type.name:20}{t.in_conditional:>5}'

        return the_str