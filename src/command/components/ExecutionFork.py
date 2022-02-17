


from dataclasses import dataclass
from typing import Iterable

from command.cmdstr.CommandWord import CommandWord
from command.cmdstr.CommandWordifier import CommandWordifier

from command.tokens.Tokens import Token
from command.cmdstr.utils import split_to_words



# maybe keep tokencombination stuff? 
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
    def __init__(self, cword: CommandWord, nword: CommandWord, wordifier: CommandWordifier):
        self.cword = cword
        self.nword = nword
        self.wordifier = wordifier
    
    def forks(self) -> Iterable[list[CommandWord]]:
        cword_vals = self.cword.get_values()
        nword_vals = self.nword.get_values()
        for cval in cword_vals:
            for nval in nword_vals:
                cwords = self.wordifier.wordify(cval)
                nwords = self.wordifier.wordify(nval)
                # okay this looks mental but its just returning
                # the current cval CommandWords, and the first CommandWord
                # from nval, plus a sentinel on the end
                sentinel = cwords[-1]
                yield cwords[:-1] + [nwords[0]] + [sentinel]
