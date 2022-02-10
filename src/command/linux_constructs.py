


from enum import Enum, auto


class Stream(Enum):
    STDIN = auto()
    STDOUT = auto()
    STDERR = auto()
    BOTH = auto()

class Tee:
    outfiles: list[str] = []
    append: bool = False

class Redirect:
    text: str
    stream: Stream
    destination: str
    append: bool = False

class StreamMerge:
    text: str
    source: Stream
    destination: Stream

