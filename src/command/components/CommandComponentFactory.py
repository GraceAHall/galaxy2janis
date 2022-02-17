



from abc import ABC, abstractmethod

from command.cmdstr.CommandWord import CommandWord
from command.cmdstr.CommandWordifier import CommandWordifier

from command.tokens.Tokens import Token, TokenType
from command.components.Flag import Flag
from command.components.Option import Option
from command.components.Positional import Positional
from command.components.ExecutionFork import ExecutionFork

from tool.param.InputParam import BoolParam, SelectParam
from tool.tool_definition import GalaxyToolDefinition

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

    def create_from_opt(self, option: Option) -> Flag:
        gxvar = option.gxvar if option.gxvar_attachment == 1 else None
        return Flag(
            prefix=option.prefix,
            cmdstr_index=len(option.presence_array), # workaround
            gxvar=gxvar
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

class CommandComponentFactory: 
    cword: CommandWord
    nword: CommandWord
    cmdstr_index: int
    """
    these values above are set using the create() method. 
    just to avoid passing around a lot
    """
    
    def __init__(self, tool: GalaxyToolDefinition):
        self.wordifier = CommandWordifier(tool) # for annoying option/bool params (have many possible values)

    def cast_to_flag(self, option: Option) -> Flag:
        spawner = FlagComponentSpawner()
        return spawner.create_from_opt(option)

    def create(self, cword: CommandWord, nword: CommandWord, cmdstr_index: int) -> list[CommandComponent]:
        self.cmdstr_index = cmdstr_index
        self.cword = cword
        self.nword = nword
        if self.is_simple_case():
            return self.make_simple()
        return self.make_complex()

    def is_simple_case(self) -> bool:
        # not galaxy options or bool param
        if self.word_is_bool_select(self.cword) or self.word_is_bool_select(self.nword):
            return False
        return True

    def word_is_bool_select(self, word: CommandWord) -> bool:
        if word.token.type == TokenType.GX_INPUT:
            match word.gxvar:
                case BoolParam() | SelectParam():
                    return True
                case _:
                    pass
        return False

    def make_simple(self) -> list[CommandComponent]:
        new_component = self.make_component(self.cword.token, self.nword.token, self.cmdstr_index)
        new_component = self.transfer_cmdword_attrs(new_component)
        return [new_component]

    def transfer_cmdword_attrs(self, component: CommandComponent) -> CommandComponent:
        match component:
            case Flag():
                component.gxvar = self.cword.gxvar
            case Option():
                if self.cword.gxvar:
                    component.gxvar = self.cword.gxvar
                elif self.nword.gxvar:
                    component.gxvar = self.nword.gxvar
            case Positional():
                component.gxvar = self.cword.gxvar
        return component

    def make_component(self, ctoken: Token, ntoken: Token, cmdstr_index: int) -> CommandComponent:
        spawner = self.select_spawner(ctoken, ntoken)
        return spawner.create(ctoken, ntoken, cmdstr_index)

    def select_spawner(self, ctoken: Token, ntoken: Token) -> ComponentSpawner:
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
    
    def make_complex(self) -> list[CommandComponent]:
        efork = ExecutionFork(self.cword, self.nword, self.wordifier)
        for fork in efork.forks():
            components += self.iter_wordtokens(fork.combination)
        return components
 
    


