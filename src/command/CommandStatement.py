


from typing import Optional
from command.linux_constructs import Tee, Redirect, StreamMerge
from command.tokens.Tokenifier import Tokenifier
from command.tokens.Tokens import Token


class CommandStatement:
    def __init__(self, cmdline: str, end_delim: Optional[str]=None):
        self.cmdline = cmdline
        self.end_delim = end_delim
        self.tokens: list[list[Token]] = []

        # later
        self.stream_merges: list[StreamMerge] = []
        self.redirects: list[Redirect] = []
        self.tees: list[Tee] = []

    def set_tokens(self, tokenifier: Tokenifier) -> None:
        pass

    def set_attrs(self) -> None:
        pass


    'abricate input > output'  
    'cp working/* outputs/*'