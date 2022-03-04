


from typing import Optional
from dataclasses import dataclass

from tool.param.Param import Param
from tool.tool_definition import GalaxyToolDefinition

from command.tokens.TokenFactory import TokenFactory
from command.tokens.Tokens import Token
import command.iterators.utils as component_utils


@dataclass
class CommandWord:
    """
    represents a space or quotes delimited section of a command string (usually just a 'word')
    token_lists is double nested list because 
    a single command word may have multiple realised
    values, and each realised value may be a single word, or a number of words. see TODO INSERT TOOLXML EXAMPLE
    """
    token: Token
    nextword_delim: str = ' '
    in_conditional: bool = False
    in_loop: bool = False

    @property
    def text(self) -> str:
        return self.token.text

    @property
    def gxvar(self) -> Optional[Param]:
        return self.token.gxvar
    
    def __repr__(self) -> str:
        return f'CommandWord(value={self.text}, token={self.token.type}, gxvar={self.gxvar})'

    def get_values(self) -> list[str]:
        if component_utils.word_is_bool_select(self):
            return self.token.gxvar.get_all_values(nonempty=True) # type: ignore
        return [self.token.text]


class CommandWordFactory:
    def __init__(self, tool: GalaxyToolDefinition):
        self.TokenFactory = TokenFactory(tool)

    def spawn_end_sentinel(self) -> CommandWord:
        token = self.TokenFactory.spawn_end_sentinel()
        sentinel_word = CommandWord(
            token=token
        )
        return sentinel_word

    def create(self, the_string: str, nextword_delim: str=' ', levels: Optional[dict[str, int]]=None) -> CommandWord:
        token = self.TokenFactory.tokenify(the_string)
        cmdword = CommandWord(token=token, nextword_delim=nextword_delim)
        self.set_levels(cmdword, levels)
        return cmdword

    def set_levels(self, cmdword: CommandWord, levels: Optional[dict[str, int]]) -> None:
        if levels:
            if levels['conditional'] > 0:
                cmdword.in_conditional = True
            if levels['loop'] > 0:
                cmdword.in_loop = True


    
    
    
