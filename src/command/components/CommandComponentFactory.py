



from abc import ABC, abstractmethod
from command.cmdstr.CommandWord import CommandWord
from command.tokens.Tokens import Token, TokenType
#from command.components.CommandComponent import CommandComponent
from command.components.Flag import Flag
from command.components.Option import Option
from command.components.Positional import Positional

CommandComponent = Flag | Option | Positional


class ComponentSpawner(ABC):
    @abstractmethod
    def create(self, ctoken: Token, ntoken: Token, cmdstr_index: int) -> CommandComponent:
        """creates a specific CommandComponent"""
        ...

class FlagComponentSpawner(ComponentSpawner):
    def create(self, ctoken: Token, ntoken: Token, cmdstr_index: int) -> Flag:
        return Flag(
            prefix=ctoken.text,
            cmdstr_index=cmdstr_index
        )

class OptionComponentSpawner(ComponentSpawner):
    def create(self, ctoken: Token, ntoken: Token, cmdstr_index: int) -> Option:
        return Option(
            prefix=ctoken.text,
            value=ntoken.text,
            cmdstr_index=cmdstr_index,
            delim=' ' # TODO change this ive split '=' and ':' delims without noting! 
        )

class PositionalComponentSpawner(ComponentSpawner):
    def create(self, ctoken: Token, ntoken: Token, cmdstr_index: int) -> Positional:
        return Positional(
            value=ctoken.text,
            cmdstr_index=cmdstr_index
        )


def make_components(cword: CommandWord, nword: CommandWord, cmdstr_index: int) -> list[CommandComponent]:
    """
    this has to reason about the components which could be created from cword and nword
    cword may have multiple realised values, each with a list of Tokens
    nword is the same.
    
    need to:
     - get all components from all combinations of execution paths for each word
     - compare these to merge some words 
     - return list of merge components

    """
    pass

def make_component(ctoken: Token, ntoken: Token, cmdstr_index: int) -> CommandComponent:
    creator = select_creator(ctoken, ntoken)
    return creator.create(ctoken, ntoken, cmdstr_index)

def select_creator(ctoken: Token, ntoken: Token) -> ComponentSpawner:
    if is_flag(ctoken, ntoken):
        return FlagComponentSpawner()
    elif is_option(ctoken, ntoken):
        return OptionComponentSpawner()
    # positional - this has to happen last, as last resort. just trust me.
    else:
        return PositionalComponentSpawner()

NON_VALUE_TOKENTYPES = set([
    TokenType.LINUX_TEE, 
    TokenType.LINUX_REDIRECT,
    TokenType.LINUX_STREAM_MERGE,
    TokenType.END_STATEMENT,
])

def is_flag(ctoken: Token, ntoken: Token) -> bool:
    if looks_like_a_flag(ctoken):
        if looks_like_a_flag(ntoken):
            return True
        elif ntoken.type in NON_VALUE_TOKENTYPES:
            return True
    return False

def looks_like_a_flag(token: Token) -> bool:
    if token.type == TokenType.RAW_STRING and token.text.startswith('-'):
        return True
    return False

def is_option(ctoken: Token, ntoken: Token) -> bool:
    """
    happens 2nd after 'is_flag()'
    already know that its not a flag, so if the current token
    looks like a flag/option, it has to be an option. 
    """
    if looks_like_a_flag(ctoken):
        return True
    return False
 





class ExecutionFork:
    def __init__(self, ctokens: list[Token], ntokens: list[Token]):
        self.ctokens = ctokens
        self.ntokens = ntokens
        self.component_factory = CommandComponentFactory()
        self.components: list[CommandComponent] = self.extract_components()
    
    def extract_components(self) -> list[CommandComponent]:
        components: list[CommandComponent] = []
        for ctoken in self.ctokens:
            for ntoken in self.ntokens:
                components.append(self.component_factory.create(ctoken, ntoken))
        return components
    
    def spawn_all_components(self, cword: CommandWord, nword: CommandWord) -> list[CommandComponent]:
        components: list[CommandComponent] = []
        for ctoken_list in cword.realised_values:
            for ntoken_list in nword.realised_values:
                new_comp = self.make_component(ctoken_list, ntoken_list)
                components.append(new_comp)
        return components
    






"""
### old

def make_flag(self, token: Token) -> Flag:
    flag = Flag(token.text)
    flag.add_token(token) 
    if token.gx_ref != '':
        flag.galaxy_object = self.get_gx_object(token)
    return flag 


def get_gx_object(self, token: Token) -> Optional[Union[ToolParameter, ToolOutput]]:
    varname, gx_object = self.param_register.get(token.gx_ref, allow_lca=True)
    if gx_object is None:
        varname, gx_object = self.out_register.get(token.gx_ref, allow_lca=True)

    return gx_object


def make_option(self, ctoken: Token, ntoken: Token, delim: str=' ', splittable: bool=True) -> Option:
    opt = Option(ctoken.text, delim=delim, splittable=splittable)
    opt.add_token(ntoken)
    if ntoken.gx_ref != '':
        opt.galaxy_object = self.get_gx_object(ntoken)
    return opt


def make_positional(self, token: Token) -> Positional:
    pos = self.positional_count
    posit = Positional(pos)
    posit.add_token(token)
    if token.gx_ref != '':
        posit.galaxy_object = self.get_gx_object(token)
    return posit
        
"""