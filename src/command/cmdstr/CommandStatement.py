

from typing import Optional

from command.cmdstr.linux_constructs import Tee, Redirect, StreamMerge
from command.tokens.Tokenifier import Tokenifier
from command.cmdstr.CommandWord import CommandWord
from command.cmdstr.CommandWordifier import CommandWordifier
from command.cmdstr.KeyValExpander import KeyValExpander
from command.tokens.Tokens import TokenType


class CommandStatement:
    def __init__(self, cmdline: str, end_delim: Optional[str]=None):
        self.cmdline = cmdline
        self.end_delim = end_delim
        self.cmdwords: list[CommandWord] = []

        # later
        self.stream_merges: list[StreamMerge] = []
        self.redirect: Optional[Redirect] = None
        self.tees: Optional[Tee] = None

    def set_cmdwords(self, tokenifier: Tokenifier) -> None:
        # expand kv pairs in cmdline
        cmdline_expanded = self.expand_cmdline_kv_pairs(tokenifier)
        self.cmdwords = self.create_cmdwords(cmdline_expanded, tokenifier)

    def expand_cmdline_kv_pairs(self, tokenifier: Tokenifier) -> str:
        kv_expander = KeyValExpander(tokenifier)
        return kv_expander.expand(self.cmdline)
    
    def create_cmdwords(self, the_string: str, tokenifier: Tokenifier) -> list[CommandWord]:
        wordifier = CommandWordifier(tokenifier)
        return wordifier.wordify(the_string)

    def set_attrs(self) -> None:
        if len(self.cmdwords) == 0:
            raise RuntimeError(f'CommandStatement has no cmdwords set. cmdline: {self.cmdline}')
        self.set_stream_merges()
        self.set_redirects()
        self.set_tees()
    
    # everything below here is kinda gross and needs a refactor
    def set_stream_merges(self) -> None:
        words_to_remove: list[int] = []
        for i, cmdword in enumerate(self.cmdwords):
            if cmdword.has_single_realised_token():
                token = cmdword.get_first_token()
                if token and token.type == TokenType.LINUX_STREAM_MERGE:
                    self.stream_merges.append(StreamMerge(cmdword.text))
                    words_to_remove.append(i)
        self.remove_cmdwords(words_to_remove)
    
    def set_redirects(self) -> None:
        words_to_remove: list[int] = []
        for i, cmdword in enumerate(self.cmdwords):
            if cmdword.has_single_realised_token():
                token = cmdword.get_first_token()
                # tee identified
                if token and token.type == TokenType.LINUX_REDIRECT:
                    words_to_remove.append(i)
                    words_to_remove.append(i + 1)
                    self.redirects = Redirect(self.cmdwords[i].text, self.cmdwords[i+1].text)
                    break
                    
    def set_tees(self) -> None:
        words_to_remove: list[int] = []
        for i, cmdword in enumerate(self.cmdwords):
            if cmdword.has_single_realised_token():
                token = cmdword.get_first_token()
                # tee identified
                if token and token.type == TokenType.LINUX_TEE:
                    words_to_remove.append(i)
                    tee = Tee()
                    while self.cmdwords[i+1].text.startswith('-'):
                        i += 1
                        tee.options.append(self.cmdwords[i].text)
                        words_to_remove.append(i)
                    while i < len(self.cmdwords):
                        i += 1
                        tee.files.append(self.cmdwords[i].text)
                        words_to_remove.append(i)
                    self.tees = tee
                    break
        self.remove_cmdwords(words_to_remove)

    def remove_cmdwords(self, indicies: list[int]) -> None:
        indicies.sort()
        for ind in reversed(indicies):
            del self.cmdwords[ind]



