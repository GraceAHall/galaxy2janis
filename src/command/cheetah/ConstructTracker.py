


"""small module which holds <command> section constructs of importance"""

from dataclasses import dataclass
from .constructs import (
    CH_OPEN_CONDITIONAL,
    CH_CLOSE_CONDITIONAL,
    CH_OPEN_LOOP,
    CH_CLOSE_LOOP,
    CH_OPEN_FUNC,
    CH_CLOSE_FUNC,
    CH_CONSTRUCTS
)


@dataclass
class OpenCloseSegment:
    name: str
    opening: set[str]
    closing: set[str] 

class ConstructTracker:
    active_line: str 

    def __init__(self):
        # default segments to track
        self.segments: list[OpenCloseSegment] = [
            OpenCloseSegment('conditional', CH_OPEN_CONDITIONAL, CH_CLOSE_CONDITIONAL),
            OpenCloseSegment('loop', CH_OPEN_LOOP, CH_CLOSE_LOOP),
            OpenCloseSegment('function', CH_OPEN_FUNC, CH_CLOSE_FUNC),
        ]
        self.segment_levels: dict[str, int] = {s.name: 0 for s in self.segments}
    
    def update(self, line: str):
        self.active_line = line
        for segment in self.segments:
            if any ([line.startswith(openstr) for openstr in segment.opening]):
                self.segment_levels[segment.name] += 1
            elif any ([line.startswith(closestr) for closestr in segment.closing]):
                self.segment_levels[segment.name] -= 1
     
    def get_levels(self) -> dict[str, int]:
        return self.segment_levels

    def is_construct_line(self, line: str) -> bool:
        if any ([line.startswith(kw) for kw in CH_CONSTRUCTS]):
            return True
        return False

    def within_banned_segment(self) -> bool:
        banned_segments = ['loop', 'function']
        if any (self.segment_levels[name] > 0 for name in banned_segments):
            return True
        return False

    # deprecated
    def is_within_construct(self) -> bool:
        level_counts = self.segment_levels.values()
        if all([count == 0 for count in level_counts]):
            if not self.is_construct_line(self.active_line):
                return False
        return True



