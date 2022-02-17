


from typing import Optional
from dataclasses import dataclass

from tool.param.Param import Param
from command.tokens.Tokenifier import Tokenifier
from command.tokens.Tokens import Token
from tool.tool_definition import GalaxyToolDefinition


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


class CommandWordFactory:
    def __init__(self, tool: GalaxyToolDefinition):
        self.tokenifier = Tokenifier(tool)

    def spawn_sentinel(self) -> CommandWord:
        token = self.tokenifier.spawn_sentinel()
        sentinel_word = CommandWord(
            token=token
        )
        return sentinel_word

    def create(self, the_string: str, nextword_delim: str=' ', levels: Optional[dict[str, int]]=None) -> CommandWord:
        token = self.tokenifier.tokenify(the_string)
        cmdword = CommandWord(token=token, nextword_delim=nextword_delim)
        self.set_levels(cmdword, levels)
        return cmdword

    def set_levels(self, cmdword: CommandWord, levels: Optional[dict[str, int]]) -> None:
        if levels:
            if levels['conditional'] > 0:
                cmdword.in_conditional = True
            if levels['loop'] > 0:
                cmdword.in_loop = True


    
    
    
