


from typing import Tuple, Optional, Union
from enum import Enum
from classes.outputs.OutputRegister import OutputRegister
from classes.params.ParamRegister import ParamRegister
from classes.params.Params import BoolParam, SelectParam

from utils.regex_utils import (
    find_unquoted,
    get_cheetah_vars, 
    get_numbers_and_strings, 
    get_quoted_numbers,
    get_raw_numbers,
    get_quoted_strings,
    get_raw_strings,
    get_linux_operators,
    get_galaxy_keywords,
    get_keyval_pairs
)




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



class Token:
    def __init__(self, text: str, statement_block: int, token_type: TokenType):
        self.text = text
        self.statement_block = statement_block
        self.type = token_type
        self.in_conditional = False
        self.in_loop = False
        self.gx_ref: str = text if token_type in [TokenType.GX_PARAM, TokenType.GX_OUT] else ''
        

    def __str__(self) -> str:
        return f'{self.text[:29]:<30}{self.gx_ref[:29]:30}{self.type.name:25}{self.in_conditional:5}{self.statement_block:>10}'



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
    def __init__(self, prefix: str, delim: str):
        self.prefix: str = prefix
        self.delim: str = delim
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



class Command:
    def __init__(self):
        self.positionals: dict[int, Positional] = {}
        self.flags: dict[str, Flag] = {}
        self.options: dict[str, Option] = {}


    def has_options(self) -> bool:
        if len(self.options) != 0:
            return True
        return False


    def get_positional_count(self) -> int:
        return len(self.positionals)


    def get_positionals(self) -> list[Positional]:
        """
        returns list of positionals in order
        """
        positionals = list(self.positionals.values())
        positionals.sort(key = lambda x: x.pos)
        return positionals
    
    
    def get_flags(self) -> list[Positional]:
        """
        returns list of flags in alphabetical order
        """
        flags = list(self.flags.values())
        flags.sort(key=lambda x: x.prefix)
        return flags
   
    
    def get_options(self) -> list[Positional]:
        """
        returns list of positionals in order
        """
        options = list(self.options.values())
        options.sort(key=lambda x: x.prefix.lstrip('-'))
        return options


    def remove_positional(self, pos: int) -> None:
        """
        removes positional and renumbers remaining positionals
        does this by just creating a new dict and moving items across
        """
        new_positionals = {}

        for key, val in self.positionals.items():
            if key == pos:
                continue
            elif key > pos:
                val.pos = val.pos - 1
                new_positionals[key - 1] = val
            else:
                new_positionals[key] = val
        
        self.positionals = new_positionals


    def update(self, ctoken: Token, ntoken: Token, param_register: ParamRegister, out_register: OutputRegister) -> None:
        skip_next = False
        
        # first linux '>' to stdout
        if self.is_stdout(ctoken, ntoken):
            self.update_outputs(ntoken, out_register)
            skip_next = True

        # flag
        elif self.is_flag(ctoken, ntoken, param_register):
            self.update_flags(ctoken)

        # option
        elif self.is_option(ctoken, ntoken, param_register):
            self.update_options(ctoken, ntoken, ' ')
            skip_next = True

        else:
            # text positional
            # this has to happen last, as last resort
            # some examples of options which don't start with '-' exist. 
            self.update_positionals(ctoken)  

        return skip_next 


    def is_stdout(self, ctoken: Token, ntoken: Token) -> bool:
        """
        """
        if ctoken.type == TokenType.LINUX_OP:
            if ntoken.type in [TokenType.RAW_STRING, TokenType.GX_OUT]:
                return True
        return False             


    def update_outputs(self, token: Token, out_register: OutputRegister) -> None:
        if token.type == TokenType.GX_OUT:
            gx_out = out_register.get(token.text)

        elif token.type == TokenType.RAW_STRING:
            gx_out = out_register.get_output_by_filepath(token.text)
        
        if gx_out is None:
            raise Exception(f"could not find gx output: {token.text}")

        gx_out.is_stdout = True


    def update_positionals(self, token: Token) -> None:
        is_after_options = self.has_options()
        pos = self.get_positional_count()
        new_positional = Positional(pos, token, is_after_options)
        self.positionals[pos] = new_positional


    def update_flags(self, token: Token) -> None:
        key = token.text

        # make entry if not exists
        if key not in self.flags:
            new_flag = Flag(key)
            self.flags[key] = new_flag
                
        self.flags[key].sources.append(token)       


    def are_identical_tokens(self, token1: Token, token2: Token) -> bool:
        if token1.text == token2.text:
            if token1.gx_ref == token2.gx_ref:
                return True
        return False


    def update_options(self, ctoken: Token, ntoken: Token, delim=' ') -> None:
        key = ctoken.text

        if key not in self.options:
            new_option = Option(key, delim)
            self.options[key] = new_option
            
        self.options[key].sources.append(ntoken)


    def is_kv_pair(self, ctoken: Token) -> bool:
        """
        https://youtu.be/hqVJpfFkJ9k
        """
        if ctoken.type == TokenType.KV_PAIR:
            return True
        return False


    def is_flag(self, ctoken: Token, ntoken: Token, param_register: ParamRegister) -> bool:
        # is this a raw flag or option?
        curr_is_raw_flag = ctoken.type == TokenType.RAW_STRING and ctoken.text.startswith('-')

        # the current token has to be a flag 
        if curr_is_raw_flag:

            # next token is a flag
            next_is_raw_flag = ntoken.type == TokenType.RAW_STRING and ntoken.text.startswith('-')
            if next_is_raw_flag:
                return True

            # next token is linux operation
            elif ntoken.type == TokenType.LINUX_OP:
                return True
            
            # next token is key-val pair
            elif ntoken.type == TokenType.KV_PAIR:
                return True
            
            # this is the last command token
            elif ntoken.type == TokenType.END_COMMAND:
                return True
                
        return False


    # def get_gx_flag_status(self, token: Token, param_register: ParamRegister) -> bool:
    #     if token.text.startswith('-'):
    #         if token.type == TokenType.GX_PARAM:        
    #             return True
    #         else:
    #             if token.gx_ref != '':
    #                 param = param_register.get(token.gx_ref)
                    
    #                 if type(param) in [BoolParam, SelectParam]:
    #                     if param.values_are_flags():
    #                         return True
        
    #     return False


    def is_option(self, ctoken: Token, ntoken: Token, param_register: ParamRegister) -> bool:
        # happens 2nd after 'is_flag()'
        # already know that its not a flag, so if the current token
        # looks like a flag/option, it has to be an option. 

        curr_is_raw_flag = ctoken.type == TokenType.RAW_STRING and ctoken.text.startswith('-')

        # the current token has to be a flag 
        if curr_is_raw_flag:
            return True
                
        return False


    def pretty_print(self) -> None:
        print('\npositionals ---------\n')
        print(f'{"pos":<10}{"text":20}{"gx_ref":20}{"token":20}{"datatype":20}{"after opts":>5}')
        for p in self.positionals.values():
            print(p)

        print('\nflags ---------------\n')
        print(f'{"text":30}{"gx_ref":30}{"token":20}{"datatype":20}{"cond":>5}')
        for f in self.flags.values():
            print(f)

        print('\noptions -------------\n')
        print(f'{"prefix":30}{"text":30}{"gx_ref":30}{"token":20}{"datatype":20}{"cond":>5}')
        for opt in self.options.values():
            print(opt)


