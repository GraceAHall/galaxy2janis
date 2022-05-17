


from __future__ import annotations
from typing import Any

from command.cheetah.blocks import get_next_block 
from command.cheetah.blocks import CheetahBlock, BlockType



class PartialCheetahEvaluator:
    def __init__(self, lines: list[str], input_dict: dict[str, Any]):
        self.lines = lines
        self.input_dict = input_dict
        self.ptr: int = 0

    def evaluate(self) -> list[str]:
        while self.ptr < len(self.lines):
            block = get_next_block(self.ptr, self.lines)
            if self.should_evaluate(block):
                block.evaluate(self.input_dict)
                self.update_lines(block)
            self.update_ptr(block)
        return self.lines
    
    def should_evaluate(self, block: CheetahBlock) -> bool:
        """dictates whether this block should be evaluated or left as original text"""
        if block.lines == ['']:
            return False
        if block.type in [BlockType.INLINE, BlockType.CONDITIONAL]:
            return True
        return False

    def update_lines(self, block: CheetahBlock) -> None:
        old_lines_top = self.lines[:block.start]
        old_lines_bottom = self.lines[block.stop + 1:]
        self.lines = old_lines_top + block.lines + old_lines_bottom
    
    def update_ptr(self, block: CheetahBlock) -> None:
        if block.evaluated:
            self.ptr += 1  # success, go to next line
        else:
            self.ptr += block.height # TODO CHECK




