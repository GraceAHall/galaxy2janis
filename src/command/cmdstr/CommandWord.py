


from typing import Iterator, Optional
from dataclasses import dataclass, field

from tool.param.Param import Param
from tool.param.InputParam import BoolParam, SelectParam
from command.cmdstr.utils import split_words
from command.tokens.Tokenifier import Tokenifier
from command.tokens.Tokens import Token, TokenType
from command.cmdstr.KeyValExpander import KeyValExpander


@dataclass
class CommandWord:
    """
    represents a space or quotes delimited section of a command string (usually just a 'word')
    token_lists is double nested list because 
    a single command word may have multiple realised
    values, and each realised value may be a single word, or a number of words. see TODO INSERT TOOLXML EXAMPLE
    """
    text: str 
    gxvar: Optional[Param] = None
    in_conditional: bool = False
    in_loop: bool = False
    token_lists: list[list[Token]] = field(default_factory=list)

    @property
    def realised_values(self) -> Iterator[list[Token]]:
        for tlist in self.token_lists:
            yield tlist

    def has_single_realised_token(self) -> bool:
        if len(self.token_lists) == 1 and len(self.token_lists[0]) == 1: 
            return True
        return False

    def get_first_token(self) -> Optional[Token]:
        if self.has_single_realised_token:
            return self.token_lists[0][0]
        return None



class CommandWordFactory:
    def __init__(self, tokenifier: Tokenifier):
        self.tokenifier = tokenifier

    def create(self, the_string: str, levels: Optional[dict[str, int]]=None) -> CommandWord:
        cmdword = CommandWord(text=the_string)
        self.set_gxvar(cmdword)
        self.set_levels(cmdword, levels)
        self.set_token_lists(cmdword)
        return cmdword

    def set_gxvar(self, cmdword: CommandWord) -> None:
        """
        annotates the gxvar attribute from the unmodified text
        necessary because some cmdwords get expanded to realised values
        need to hold on to the original gxvar in these cases
        """
        text_token = self.tokenifier.tokenify(cmdword.text)
        cmdword.gxvar = text_token.gxvar

    def set_levels(self, cmdword: CommandWord, levels: Optional[dict[str, int]]) -> None:
        if levels:
            if levels['conditional'] > 0:
                cmdword.in_conditional = True
            if levels['loop'] > 0:
                cmdword.in_loop = True

    def set_token_lists(self, cmdword: CommandWord) -> None:
        primary_token = self.tokenifier.tokenify(cmdword.text)
        if self.should_expand(primary_token):
            token_lists = self.expand_galaxy_tokens(primary_token)
        else:
            token_lists = [[primary_token]]
        cmdword.token_lists = token_lists
    
    def should_expand(self, token: Token) -> bool:
        if token.type == TokenType.GX_INPUT:
            if isinstance(token.gxvar, BoolParam) or isinstance(token.gxvar, SelectParam):
                return True
        return False

    def expand_galaxy_tokens(self, token: Token) -> list[list[Token]]:
        gxvar: BoolParam | SelectParam = token.gxvar # type: ignore
        values = gxvar.get_all_values()
        values = [v for v in values if v != '']
        return [self.tokenify_galaxy_value(val) for val in values]
    
    def tokenify_galaxy_value(self, value: str) -> list[Token]:
        kv_expander = KeyValExpander(self.tokenifier)
        expanded_value = kv_expander.expand(value)
        words = split_words(expanded_value)
        return [self.tokenifier.tokenify(word) for word in words]



