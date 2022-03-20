

from command.tokens.Tokens import Token

from enum import Enum, auto

class Stream(Enum):
    STDIN = auto()
    STDOUT = auto()
    STDERR = auto()
    BOTH = auto()


class StreamMerge:
    def __init__(self, token: Token):
        self.token = token
        self.source: Stream = self.extract_source()
        self.destination: Stream = self.extract_dest()

    def extract_source(self) -> Stream:
        if self.token.text[0] == '2':
            return Stream.STDERR
        return Stream.STDOUT

    def extract_dest(self) -> Stream:
        if self.token.text[-1] == '2':
            return Stream.STDERR
        return Stream.STDOUT
