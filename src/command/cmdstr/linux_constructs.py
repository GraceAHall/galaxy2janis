


from enum import Enum, auto




class Stream(Enum):
    STDIN = auto()
    STDOUT = auto()
    STDERR = auto()
    BOTH = auto()

class Tee:
    options: list[str] = []
    files: list[str] = []


class Redirect:
    def __init__(self, redirect: str, file: str):
        self.text = redirect + ' ' + file
        self.file = file
        self.append: bool = True if redirect == '>>' else False
        self.stream: Stream = self.extract_stream()

    def extract_stream(self) -> Stream:
        match self.text[0]:
            case '2':
                return Stream.STDERR
            case _:
                return Stream.STDOUT


class StreamMerge:
    def __init__(self, text: str):
        self.text = text
        self.source: Stream = self.extract_source()
        self.destination: Stream = self.extract_dest()

    def extract_source(self) -> Stream:
        if self.text[0] == '2':
            return Stream.STDERR
        return Stream.STDOUT

    def extract_dest(self) -> Stream:
        if self.text[-1] == '2':
            return Stream.STDERR
        return Stream.STDOUT

