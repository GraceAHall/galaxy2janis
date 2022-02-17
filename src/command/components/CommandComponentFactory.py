



from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable

from command.cmdstr.CommandWord import CommandWord
from command.cmdstr.CommandWordifier import CommandWordifier

from command.tokens.Tokens import Token, TokenType
from command.components.Flag import Flag
from command.components.Option import Option
from command.components.Positional import Positional
from tool.tool_definition import GalaxyToolDefinition

CommandComponent = Flag | Option | Positional




@dataclass
class WordToken:
    word: str
    token: Token

class TokenCombination:
    def __init__(self, ctoken_list: list[Token], ntoken_list: list[Token]):
        self.ctoken_list = ctoken_list
        self.ntoken_list = ntoken_list
    
    @property
    def combination(self) -> list[WordToken]:
        new_comb: list[WordToken] = []
        new_comb += [WordToken('current', ctoken) for ctoken in self.ctoken_list]
        new_comb += [WordToken('next', ntoken) for ntoken in self.ntoken_list]
        return new_comb
        

class ExecutionFork:
    def __init__(self, cword: CommandWord, nword: CommandWord):
        self.cword = cword
        self.nword = nword
    
    def forks(self) -> Iterable[TokenCombination]:
        pass
        # for ctoken_list in self.cword.realised_values:
        #     for ntoken_list in self.nword.realised_values:
        #         yield TokenCombination(ctoken_list, ntoken_list)

    



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


NON_VALUE_TOKENTYPES = set([
    TokenType.LINUX_TEE, 
    TokenType.LINUX_REDIRECT,
    TokenType.LINUX_STREAM_MERGE,
    TokenType.END_SENTINEL,
])


def should_expand(self, token: Token) -> bool:
    if token.type == TokenType.GX_INPUT:
        if isinstance(token.gxvar, BoolParam) or isinstance(token.gxvar, SelectParam):
            return True
    return False

def expand_galaxy_tokens(self, token: Token) -> list[list[Token]]:
    gxvar: BoolParam | SelectParam = token.gxvar # type: ignore
    optvals = gxvar.get_all_values()
    optvals = [v for v in optvals if v != '']
    optvals = self.format_kv_values(optvals)
    return [self.tokenify_option_value(val) for val in optvals]


class CommandComponentFactory: 
    def __init__(self, tool: GalaxyToolDefinition):
        self.wordifier = CommandWordifier(tool) # this wordifier is just 

    def create(self, cword: CommandWord, nword: CommandWord) -> list[CommandComponent]:
        if self.is_simple_case(cword, nword):
            return self.make_single(cword, nword)
        return self.make_multiple(cword, nword)

    def is_simple_case(self, cword: CommandWord, nword: CommandWord) -> bool:
        # not galaxy options or bool param
        if cword.token.type not in [TokenType.GX_INPUT, TokenType.GX_OUTPUT]:
             

        if cword.has_single_realised_token() and nword.has_single_realised_token():
            return True
        return False

    def make_single(self, cword: CommandWord, nword: CommandWord) -> list[CommandComponent]:
        pass

    def make_multiple(self, cword: CommandWord, nword: CommandWord) -> list[CommandComponent]:
        components: list[CommandComponent] = []
        efork = ExecutionFork(cword, nword)
        for fork in efork.forks():
            components += self.iter_wordtokens(fork.combination)
        return components

    def iter_wordtokens(self, wordtokens: list[WordToken]) -> list[CommandComponent]:
        components: list[CommandComponent] = []

        i = 0
        while i < len(wordtokens) - 1:
            step_size = 1
            cwt = wordtokens[i]
            nwt = wordtokens[i + 1]
            new_comp = self.make_component(cwt, nwt)
            if isinstance(new_comp, Option):
                step_size = 2
            i += step_size
        return components

    def make_component(self, ctoken: Token, ntoken: Token, cmdstr_index: int) -> CommandComponent:
        creator = self.select_creator(ctoken, ntoken)
        return creator.create(ctoken, ntoken, cmdstr_index)

    def select_creator(self, ctoken: Token, ntoken: Token) -> ComponentSpawner:
        if self.is_flag(ctoken, ntoken):
            return FlagComponentSpawner()
        elif self.is_option(ctoken, ntoken):
            return OptionComponentSpawner()
        # positional - this has to happen last, as last resort. just trust me.
        else:
            return PositionalComponentSpawner()

    def is_flag(self, ctoken: Token, ntoken: Token) -> bool:
        if self.looks_like_a_flag(ctoken):
            if self.looks_like_a_flag(ntoken):
                return True
            elif ntoken.type in NON_VALUE_TOKENTYPES:
                return True
        return False

    def looks_like_a_flag(self, token: Token) -> bool:
        if token.type == TokenType.RAW_STRING and token.text.startswith('-'):
            return True
        return False

    def is_option(self, ctoken: Token, ntoken: Token) -> bool:
        """
        happens 2nd after 'is_flag()'
        already know that its not a flag, so if the current token
        looks like a flag/option, it has to be an option. 
        """
        if self.looks_like_a_flag(ctoken):
            return True
        return False
 


"""
def create_old(self, cword: CommandWord, nword: CommandWord) -> list[CommandComponent]:
    if self.is_simple_case(cword, nword):
        return self.make_single(cword, nword)
    return self.make_multiple(cword, nword)

def is_simple_case(self, cword: CommandWord, nword: CommandWord) -> bool:
    if cword.has_single_realised_token() and nword.has_single_realised_token():
        return True
    return False

def make_single(self, cword: CommandWord, nword: CommandWord) -> list[CommandComponent]:
    # for when cword and nword each have a single token
    efork = ExecutionFork(cword, nword)
    for t_combination in efork.combinations():
        pass

def make_multiple(self, cword: CommandWord, nword: CommandWord) -> list[CommandComponent]:
    # for when cword and nword have multiple token possibilities
    pass


def make_components(cword: CommandWord, nword: CommandWord, cmdstr_index: int) -> list[CommandComponent]:
    
    # this has to reason about the components which could be created from cword and nword
    # cword may have multiple realised values, each with a list of Tokens
    # nword is the same.
    
    # need to:
    #  - get all components from all combinations of execution paths for each word
    #  - compare these to merge some words 
    #  - return list of merge components

    
    pass

    def extract_components(self) -> list[CommandComponent]:
        components: list[CommandComponent] = []
        for ctoken in self.ctokens:
            for ntoken in self.ntokens:
                components.append(self.component_factory.create(ctoken, ntoken))
        return components
    
    def spawn_all_components(self, cword: CommandWord, nword: CommandWord) -> list[CommandComponent]:
        components: list[CommandComponent] = []

                new_comp = self.make_component(ctoken_list, ntoken_list)
                components.append(new_comp)
        return components



"""






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