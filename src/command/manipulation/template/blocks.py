


from __future__ import annotations
from uuid import uuid4
from dataclasses import dataclass
from command.cmdstr.ConstructTracker import ConstructTracker


def get_blocks(lines: list[str]) -> list[CheetahBlock]:
    factory = BlockFactory(lines=lines, indent_level=0)
    return factory.produce()

def get_child_blocks(lines: list[str]) -> list[CheetahBlock]:
    assert(get_blocks(lines) == 1)
    factory = BlockFactory(lines=lines, indent_level=1)
    return factory.produce()


@dataclass
class BlockLine:
    line_num: int
    level: int
    text: str

class BlockFactory:
    def __init__(self, lines: list[str], indent_level: int):
        self.lines = lines
        self.indent_level = indent_level
        self.blocks_levels: dict[int, list[CheetahBlock]] = {}
        self.construct_tracker: ConstructTracker = ConstructTracker()

    def produce(self) -> list[CheetahBlock]:
        """
        gets all cheetah blocks from lines
        """
        if len(self.lines) == 0:
            return []
        else:
            self.set_blocks_levels()
            return self.blocks_levels[self.indent_level]

    def set_blocks_levels(self) -> None:
        lines: list[BlockLine] = []
        for i, line in enumerate(self.lines):
            self.construct_tracker.update(line)
            # lines.append(BlockLine(
            #     line_num=i,
            #     level=
            # ))





@dataclass
class CheetahBlock:
    """
    The smallest unit of evaluatable cheetah logic
    examples: single line statement, conditional block, loop block
    """
    line_start: int
    line_stop: int
    lines: list[str] 

    def __post_init__(self):
        self.uuid: str = str(uuid4())
        self.evaluated: bool = False

    @property
    def child_blocks(self) -> list[CheetahBlock]:
        """returns next level of cheetah blocks within this block"""
        return get_child_blocks(self.lines)

    @property  # unsure if needed
    def height(self) -> int:
        return self.line_stop - self.line_start + 1

    def set_lines(self, lines: list[str]) -> None:
        self.lines = lines

    def replace_child_block(self, block: CheetahBlock) -> None:
        old_lines_top = self.lines[:block.line_start]
        old_lines_bottom = self.lines[block.line_stop+1:]
        self.lines = old_lines_top + block.lines + old_lines_bottom
