

from enum import Enum, auto
from command.tokens.Tokens import Token
from tool.param.OutputParam import DataOutputParam, CollectionOutputParam
from tool.parsing.selectors import Selector


class Stream(Enum):
    STDIN = auto()
    STDOUT = auto()
    STDERR = auto()
    BOTH = auto()

class Tee:
    options: list[Token] = []
    files: list[Token] = []


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


class Redirect:
    def __init__(self, redirect: Token, file: Token):
        self.redirect = redirect
        self.file = file
        self.append: bool = True if redirect.text == '>>' else False
        self.stream: Stream = self.extract_stream()

    @property
    def text(self) -> str:
        return self.redirect.text + ' ' + self.file.text

    def extract_stream(self) -> Stream:
        match self.redirect.text[0]:
            case '2':
                return Stream.STDERR
            case _:
                return Stream.STDOUT
    
    def is_optional(self) -> bool:
        # NOTE - janis does not allow optional outputs
        return False

    def is_array(self) -> bool:
        match self.file.gxvar:
            case CollectionOutputParam() | DataOutputParam():
                return self.file.gxvar.is_array()
            case _:
                pass
        return False

    def get_selector(self) -> Selector:
        match self.file.gxvar:
            case CollectionOutputParam() | DataOutputParam():
                if self.file.gxvar.selector:
                    return self.file.gxvar.selector
            case _:
                pass
        raise RuntimeError(f'no selector for {self.text}')

