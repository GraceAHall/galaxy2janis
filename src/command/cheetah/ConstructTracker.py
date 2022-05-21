


"""small module which holds <command> section constructs of importance"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Tuple
from uuid import uuid4
from .constructs import (
    CH_OPEN_CONDITIONAL,
    CH_CLOSE_CONDITIONAL,
    CH_OPEN_LOOP,
    CH_CLOSE_LOOP,
    CH_OPEN_FUNC,
    CH_CLOSE_FUNC,
    CH_CONSTRUCTS
)


class ConstructType(Enum):
    CONDITIONAL = auto()
    LOOP        = auto()
    FUNCTION    = auto()


@dataclass
class Construct:
    subtype: ConstructType
    
    def __post_init__(self):
        self.lines: list[str] = []
        self.uuid: str = str(uuid4())

# construct subtypes and their opening / closing cheetah tags (for identification in text)
constructs_opens_closes: list[Tuple[ConstructType, set[str], set[str]]] = [
    (ConstructType.CONDITIONAL, CH_OPEN_CONDITIONAL, CH_CLOSE_CONDITIONAL),
    (ConstructType.LOOP, CH_OPEN_LOOP, CH_CLOSE_LOOP),
    (ConstructType.FUNCTION, CH_OPEN_FUNC, CH_CLOSE_FUNC),
]


class ConstructStack:
    def __init__(self):
        self.stack: list[Construct] = []
    
    def add(self, construct: Construct) -> None:
        self.stack.append(construct)
    
    def pop(self, subtype: ConstructType) -> None:
        if self.depth > 0:
            assert(self.current_construct)
            assert(self.current_construct.subtype == subtype)
            self.stack.pop()

    @property
    def depth(self) -> int:
        return len(self.stack)
    
    @property
    def current_construct(self) -> Optional[Construct]:
        if len(self.stack) > 0:
            return self.stack[-1]
        return None

    def within_construct(self, ctype: ConstructType) -> bool:
        for construct in self.stack:
            if construct.subtype == ctype:
                return True
        return False


class ConstructTracker:

    def __init__(self):
        self.stack: ConstructStack = ConstructStack()
    
    # methods to manage construct stack
    def update(self, line: str):
        self.handle_entering_constructs(line)
        self.handle_line(line)
        self.handle_leaving_constructs(line)

    def handle_entering_constructs(self, line: str) -> None:
        for subtype, openings, _ in constructs_opens_closes:
            if any ([line.startswith(openstr) for openstr in openings]):
                construct = Construct(subtype)
                self.stack.add(construct)

    def handle_line(self, line: str) -> None:
        if self.stack.current_construct: 
            self.stack.current_construct.lines.append(line)

    def handle_leaving_constructs(self, line: str) -> None:
        for subtype, _, closings in constructs_opens_closes:
            if any ([line.startswith(closestr) for closestr in closings]):
                self.stack.pop(subtype)

    @property
    def within_conditional(self) -> bool:
        if self.stack.within_construct(ConstructType.CONDITIONAL):
            return True
        return False
    
    @property
    def within_loop(self) -> bool:
        if self.stack.within_construct(ConstructType.LOOP):
            return True
        return False
    
    @property
    def within_banned_segment(self) -> bool:
        banned_constructs = [ConstructType.LOOP, ConstructType.FUNCTION]
        for construct in banned_constructs: 
            if self.stack.within_construct(construct):
                return True
        return False

    def active_is_boundary(self, line: str) -> bool:
        if any ([line.startswith(kw) for kw in CH_CONSTRUCTS]):
            return True
        return False

