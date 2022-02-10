


from dataclasses import dataclass, field
from command.linux_constructs import Tee, Redirect, StreamMerge
from command.tokens.Tokens import Token


@dataclass
class CommandStatement:
    raw_string: str
    tokens: list[list[Token]] = field(default_factory=list)
    tees: list[Tee] = field(default_factory=list)
    stream_merges: list[StreamMerge] = field(default_factory=list)
    redirects: list[Redirect] = field(default_factory=list)


    