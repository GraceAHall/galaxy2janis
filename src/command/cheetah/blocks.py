


from __future__ import annotations
from enum import Enum, auto
from uuid import uuid4
from dataclasses import dataclass
from command.cheetah.ConstructTracker import ConstructTracker
from command.cheetah.constructs import (
    CH_OPEN_CONDITIONAL,
    CH_OPEN_LOOP,
    CH_OPEN_FUNC,
    LINUX_ALIAS,
    CH_ENV
)


def get_blocks(offset: int, lines: list[str], indent_level: int) -> list[CheetahBlock]:
    block_lines = LineFactory(lines).get_lines()
    factory = BlockFactory(offset, block_lines, indent_level)
    return factory.get_blocks()


@dataclass
class BlockLine:
    line_num: int
    indent: int
    text: str

class LineFactory:
    """creates BlockLines from normal text lines"""

    def __init__(self, lines: list[str]):
        self.text_lines = lines
        self.block_lines: list[BlockLine] = []
        self.construct_tracker: ConstructTracker = ConstructTracker()

    def get_lines(self) -> list[BlockLine]:
        if len(self.text_lines) == 0:
            return []
        else:
            for i, line in enumerate(self.text_lines):
                self.add_block_line(i, line)
            return self.block_lines

    def add_block_line(self, i: int, line: str) -> None:
        levels = self.construct_tracker.get_levels()
        indent = self.calculate_indent(levels)
        self.construct_tracker.update(line) # LEAVE THIS HERE
        block_line = BlockLine(
            line_num=i,
            indent=indent,
            text=line
        )
        self.block_lines.append(block_line)
    

    
    def calculate_indent(self, construct_levels: dict[str, int]) -> int:
        return sum(construct_levels.values())
    
    

class BlockFactory:
    """
    gets all cheetah blocks occurring in self.lines on a particular 
    indent level
    """
    def __init__(self, offset: int, block_lines: list[BlockLine], indent_level: int):
        self.offset = offset
        self.block_lines = block_lines
        self.target_indent = indent_level
        self.active_lines: list[BlockLine] = []
        self.blocks: list[CheetahBlock] = []

    def get_blocks(self) -> list[CheetahBlock]:
        for line in self.block_lines:
            if self.start_block(line): # new block begins
                self.add_block() # add previous block
                self.active_lines = [] # reset active lines
            if self.within_block(line):
                self.active_lines.append(line)
        self.add_block()
        return self.blocks

    def start_block(self, line: BlockLine) -> bool:
        if line.indent == self.target_indent:
            return True
        return False
    
    def within_block(self, line: BlockLine) -> bool:
        if line.indent >= self.target_indent:
            return True
        return False

    def add_block(self) -> None:
        if self.active_lines:
            block = CheetahBlock(
                type=self.select_block_type(),
                offset=self.offset,
                relative_start=self.active_lines[0].line_num,
                relative_stop=self.active_lines[-1].line_num,
                lines=[ln.text for ln in self.active_lines]
            )
            self.blocks.append(block)
    
    def select_block_type(self) -> BlockType:
        line = self.active_lines[0].text
        types = [
            (CH_OPEN_CONDITIONAL, BlockType.CONDITIONAL),
            (CH_OPEN_LOOP, BlockType.LOOP),
            (CH_OPEN_FUNC, BlockType.FUNCTION),
            (CH_ENV, BlockType.INLINE_CH),
            (LINUX_ALIAS, BlockType.INLINE_ALIAS),
        ]
        for construct, block_type in types:
            if any ([line.startswith(text) for text in construct]):
                return block_type
        return BlockType.INLINE



class BlockType(Enum):
    MAIN            = auto()
    INLINE          = auto()
    INLINE_CH       = auto()
    INLINE_ALIAS    = auto()
    CONDITIONAL     = auto()
    FUNCTION        = auto()
    LOOP            = auto()


@dataclass
class CheetahBlock:
    """
    The smallest unit of evaluatable cheetah logic
    examples: single line statement, conditional block, loop block
    """
    type: BlockType
    offset: int
    relative_start: int
    relative_stop: int
    lines: list[str] 

    def __post_init__(self):
        self.uuid: str = str(uuid4())
        self.evaluated: bool = False

    @property
    def real_start(self) -> int:
        return self.offset + self.relative_start
    
    @property
    def real_stop(self) -> int:
        return self.offset + self.relative_stop

    @property
    def child_blocks(self) -> list[CheetahBlock]:
        """returns next level of cheetah blocks within this block"""
        if self.type in [BlockType.INLINE, BlockType.INLINE_ALIAS, BlockType.INLINE_CH]:
            return []
        return get_blocks(
            offset=self.offset + self.relative_start, 
            lines=self.lines, 
            indent_level=self.child_block_indent
        )

    @property
    def child_block_indent(self) -> int:
        if self.type == BlockType.MAIN:
            return 0  # kind of like no parent block?
        return 1

    @property  # unsure if needed
    def height(self) -> int:
        return self.relative_stop - self.relative_start + 1

    def set_lines(self, lines: list[str]) -> None:
        self.lines = lines

    # def replace_child_block(self, block: CheetahBlock) -> None:
    #     old_lines_top = self.lines[:block.line_start]
    #     old_lines_bottom = self.lines[block.line_stop+1:]
    #     self.lines = old_lines_top + block.lines + old_lines_bottom
