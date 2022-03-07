



from typing import Optional

from command.tokens.Tokens import Token, TokenType
from command.components.linux_constructs import Tee, Redirect, StreamMerge
from command.regex import scanners as scanners

class ExecutionPath:
    id: int

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.stream_merges: list[StreamMerge] = []
        self.redirect: Optional[Redirect] = None
        self.tees: Optional[Tee] = None
        self.tokens_to_excise: list[int] = []
        self.set_attrs()

    def set_attrs(self) -> None:
        self.set_stream_merges()
        self.set_redirect()
        self.set_tee()
    
    def set_stream_merges(self) -> None:
        for word_ptr, token in enumerate(self.tokens):
            if token.type == TokenType.LINUX_STREAM_MERGE:
                self.handle_stream_merge(word_ptr)
        self.excise_tokens()

    def handle_stream_merge(self, word_ptr: int) -> None:
        token = self.tokens[word_ptr]
        self.stream_merges.append(StreamMerge(token))
        self.tokens_to_excise.append(word_ptr)
    
    def set_redirect(self) -> None:
        for word_ptr, token in enumerate(self.tokens):
            if token.type == TokenType.LINUX_REDIRECT:
                self.handle_redirect(word_ptr)
                break
        self.excise_tokens()
    
    def handle_redirect(self, word_ptr: int) -> None:
        """
        handles an identified redirect. 
        creates Redirect() and marks corresponding CommandWords for removal
        """
        redirect_token = self.tokens[word_ptr]
        file_token = self.tokens[word_ptr + 1]
        if redirect_token and file_token:
            self.redirect = Redirect(redirect_token, file_token)
            self.tokens_to_excise.append(word_ptr)
            self.tokens_to_excise.append(word_ptr + 1)
                    
    def set_tee(self) -> None:
        for word_ptr, token in enumerate(self.tokens):
            if token.type == TokenType.LINUX_TEE:
                self.handle_tee(word_ptr)
                break
        self.excise_tokens()

    def handle_tee(self, word_ptr: int) -> None:
        self.tokens_to_excise.append(word_ptr)
        tee = Tee()

        # tee options
        while self.tokens[word_ptr+1].text.startswith('-'):
            word_ptr += 1
            token = self.tokens[word_ptr]
            if token:
                tee.options.append(token)
                self.tokens_to_excise.append(word_ptr)
        
        # tee files
        while word_ptr < len(self.tokens):
            word_ptr += 1
            token = self.tokens[word_ptr]
            if token:
                tee.files.append(token)
                self.tokens_to_excise.append(word_ptr)
                
        self.tee = tee

    def excise_tokens(self, elements: Optional[list[int]]=None) -> None:
        if not elements:
            elements = self.tokens_to_excise
        for ind in elements:
            matches = scanners.get_all('excision')
            self.tokens[ind] = Token(matches[0], TokenType.EXCISION)
        self.tokens_to_excise = []

