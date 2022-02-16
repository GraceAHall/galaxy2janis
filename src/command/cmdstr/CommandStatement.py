

from typing import Optional

from command.components.linux_constructs import Tee, Redirect, StreamMerge
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
        # features 
        self.stream_merges: list[StreamMerge] = []
        self.redirect: Optional[Redirect] = None
        self.tees: Optional[Tee] = None
        self.words_to_remove: list[int] = []

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
        self.set_redirect()
        self.set_tee()
    
    # the below could probably do with a refactor
    def set_stream_merges(self) -> None:
        for word_ptr, cmdword in enumerate(self.cmdwords):
            if cmdword.has_single_realised_token():
                token = cmdword.get_first_token()
                if token and token.type == TokenType.LINUX_STREAM_MERGE:
                    self.handle_stream_merge(word_ptr)
        self.flush_cmdwords()

    def handle_stream_merge(self, word_ptr: int) -> None:
        token = self.cmdwords[word_ptr].get_first_token()
        if token:
            self.stream_merges.append(StreamMerge(token))
            self.words_to_remove.append(word_ptr)
    
    def set_redirect(self) -> None:
        for word_ptr, cmdword in enumerate(self.cmdwords):
            if cmdword.has_single_realised_token():
                token = cmdword.get_first_token()
                if token and token.type == TokenType.LINUX_REDIRECT:
                    self.handle_redirect(word_ptr)
                    break
        self.flush_cmdwords()
    
    def handle_redirect(self, word_ptr: int) -> None:
        """
        handles an identified redirect. 
        creates Redirect() and marks corresponding CommandWords for removal
        """
        redirect_token = self.cmdwords[word_ptr].get_first_token()
        file_token = self.cmdwords[word_ptr + 1].get_first_token()
        if redirect_token and file_token:
            self.redirect = Redirect(redirect_token, file_token)
            self.words_to_remove.append(word_ptr)
            self.words_to_remove.append(word_ptr + 1)
                    
    def set_tee(self) -> None:
        for word_ptr, cmdword in enumerate(self.cmdwords):
            if cmdword.has_single_realised_token():
                token = cmdword.get_first_token()
                # tee identified
                if token and token.type == TokenType.LINUX_TEE:
                    self.handle_tee(word_ptr)
                    break
        self.flush_cmdwords()

    def handle_tee(self, word_ptr: int) -> None:
        self.words_to_remove.append(word_ptr)
        tee = Tee()

        # tee options
        while self.cmdwords[word_ptr+1].text.startswith('-'):
            word_ptr += 1
            token = self.cmdwords[word_ptr].get_first_token()
            if token:
                tee.options.append(token)
                self.words_to_remove.append(word_ptr)
        
        # tee files
        while word_ptr < len(self.cmdwords):
            word_ptr += 1
            token = self.cmdwords[word_ptr].get_first_token()
            if token:
                tee.files.append(token)
                self.words_to_remove.append(word_ptr)
                
        self.tee = tee

    def flush_cmdwords(self) -> None:
        self.words_to_remove.sort()
        for ind in reversed(self.words_to_remove):
            del self.cmdwords[ind]
        self.words_to_remove = []



