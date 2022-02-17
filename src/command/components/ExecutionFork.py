


from dataclasses import dataclass
from typing import Iterable

from command.cmdstr.CommandWord import CommandWord

from command.tokens.Tokens import Token
from command.components.Flag import Flag
from command.components.Option import Option
from command.components.Positional import Positional

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
