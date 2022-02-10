


from command.linux_constructs import Tee, Redirect, StreamMerge
from command.tokens.Tokens import Token


class CommandStatement:
    def __init__(self, raw_string: str):
        self.raw_string = raw_string
        self.tokens: list[list[Token]] = []
        
        # L8R
        self.stream_merges: list[StreamMerge] = []
        self.redirects: list[Redirect] = []
        self.tees: list[Tee] = []


    