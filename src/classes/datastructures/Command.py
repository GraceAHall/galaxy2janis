


from typing import Tuple, Optional, Union
from enum import Enum



from classes.datastructures.Params import Param
from classes.datastructures.Outputs import Output



class TokenType(Enum):
    GX_PARAM        = 0
    GX_OUT          = 1
    QUOTED_STRING   = 2
    RAW_STRING      = 3
    QUOTED_NUM      = 4
    RAW_NUM         = 5
    LINUX_OP        = 6
    GX_KEYWORD      = 7
    KV_PAIR         = 8
    END_COMMAND     = 9


# TODO HERE IM HERE
# restructure so that gx params get split when tokenizing the command words
# no reason to do it later, and allows the new Token datastructure (below)

class Token:
    def __init__(self, cmd_value: str, token_type: TokenType):
        self.cmd_value = cmd_value
        self.realised_value = cmd_value
        self.type = token_type
        self.in_conditional = False


    def get_repr(self) -> dict[str, str]:
        """
        """
        if self.type == TokenType.GX_PARAM:
            res_value = self.value.get_default() or ''
            cmd_value = '$' + self.value.gx_var
        elif self.type == TokenType.GX_OUT:
            res_value = ''
            cmd_value = '$' + self.value.gx_var
        else:
            res_value = self.value
            cmd_value = self.value

        representation = {
            'res_value': res_value,
            'cmd_value': cmd_value,
            'type': self.type.name,
            'in_cond': self.in_conditional 
        }

        return representation
   



"""
Maybe these should be Structs? 
"""

"""
Positionals have a single argument and a position
Shouldn't be settable from a galaxy param
Linux operators count as Positionals
"""

class Positional:
    def __init__(self, pos: int, token: Token, after_options: bool):
        self.pos = pos
        self.token = token
        self.after_options = after_options
        self.is_optional: bool = False
        self.datatypes: list[str] = []


    def set_is_conditional(self) -> bool:
        return self.token.in_conditional


    def __str__(self) -> str:
        props = self.token.get_repr()
        return f'{self.pos:<10}{props["res_value"][:19]:20}{props["cmd_value"][:19]:20}{props["type"][:19]:20}{",".join(self.datatypes):20}{self.after_options:>5}'


"""
Flags have a text element and sources
Flags arguments can be included in the command string via sources
Valid sources are RAW_STRING and GX_PARAM 
"""
class Flag:
    def __init__(self, prefix: str):
        self.prefix: str = prefix
        self.sources: list[Token] = [] 
        self.is_optional: bool = False
        self.datatypes: list[str] = []


    def set_is_conditional(self) -> bool:
        for source in self.sources:
            if not source.is_conditional:
                return False
                
        return True


    def __str__(self) -> str:
        """
        print(f'{"prefix":30}{"token type":>20}')
        """
        
        the_str = ''

        props = self.sources[0].get_repr()
        the_str += f'{self.prefix[:29]:30}{props["cmd_value"][:29]:30}{props["type"]:20}{",".join(self.datatypes):20}{props["in_cond"]:>5}'

        if len(self.sources) > 1:
            for source in self.sources[1:]:
                props = source.get_repr()
                the_str += f'\n{"":30}{props["cmd_value"][:29]:30}{props["type"]:20}{",".join(self.datatypes):20}{props["in_cond"]:>5}'

        return the_str


"""
Options have a flag and an argument 
prefix can be set from a RAW_STRING and/or GX_PARAM?
Sources can be set from just about anything 

sources has a little bit different meaning to as seen in Flags.

"""
class Option:
    def __init__(self, prefix: str, delim: str):
        self.prefix: str = prefix
        self.delim: str = delim
        self.sources: list[Token] = []
        self.is_optional: bool = False
        self.datatypes: list[str] = []


    def set_is_conditional(self) -> bool:
        for source in self.sources:
            if not source.is_conditional:
                return False

        return True


    def __str__(self) -> str:
        """
        {"prefix":30}{"token text":30}{"token gx_var":30}{"token type":>10}
        """
        the_str = ''

        props = self.sources[0].get_repr()
        the_str += f'{self.prefix[:29]:30}{props["res_value"][:29]:30}{props["cmd_value"][:29]:30}{props["type"]:20}{",".join(self.datatypes):20}{props["in_cond"]:>5}'

        if len(self.sources) > 1:
            for source in self.sources[1:]:
                props = source.get_repr()
                the_str += f'\n{"":30}{props["res_value"][:29]:30}{props["cmd_value"][:29]:30}{props["type"]:20}{",".join(self.datatypes):20}{props["in_cond"]:>5}'

        return the_str



class Command:
    def __init__(self):
        self.positionals: dict[int, Positional] = {}
        self.flags: dict[str, Flag] = {}
        self.options: dict[str, Option] = {}


    def update_positionals(self, pos: int, token: Token, after_options: bool) -> None:
        new_positional = Positional(pos, token, after_options)
        self.positionals[pos] = new_positional


    def update_flags(self, token: Token) -> None:
        props = token.get_repr()
        key = props['res_value']

        if key not in self.flags:
            new_flag = Flag(key)
            self.flags[key] = new_flag
            
        self.flags[key].sources.append(token)       


    def update_options(self, flag_token: Token, arg_token: Token, delim: str) -> None:
        props = flag_token.get_repr()
        key = props['res_value']

        if key not in self.options:
            new_option = Option(key, delim)
            self.options[key] = new_option
        self.options[key].sources.append(arg_token)


    


    def pretty_print(self) -> None:
        print('\npositionals ---------\n')
        print(f'{"pos":<10}{"resolved value":20}{"command value":20}{"token":20}{"datatype":20}{"after opts":>5}')
        for p in self.positionals.values():
            print(p)

        print('\nflags ---------------\n')
        print(f'{"prefix":30}{"command value":30}{"token":20}{"datatype":20}{"cond":>5}')
        for f in self.flags.values():
            print(f)

        print('\noptions -------------\n')
        print(f'{"prefix":30}{"resolved value":30}{"command value":30}{"token":20}{"datatype":20}{"cond":>5}')
        for opt in self.options.values():
            print(opt)


