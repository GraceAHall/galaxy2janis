


from __future__ import annotations
from typing import Any, Optional
from Cheetah.Template import Template

import command.manipulation.utils as utils
from command.cheetah.blocks import CheetahBlock, BlockType, get_blocks

from command.cheetah.constructs import (
    CH_WITHIN_CONDITIONAL,
    CH_CLOSE_CONDITIONAL,
    CH_CLOSE_LOOP,
    CH_CLOSE_FUNC,
)
IGNORE_CONSTRUCTS = CH_WITHIN_CONDITIONAL | CH_CLOSE_CONDITIONAL | CH_CLOSE_LOOP | CH_CLOSE_FUNC



"""
TODO tomorrow
this should just update self.lines
single source of truth that gets updated as we go
for #else #elif etc within constructs - ignore these 'blocks'.

"""




class SectionalCheetahEvaluator:
    """
    evaluates a cheetah template with a supplied input_dict.
    returns the output str, or None if fails
    recursive
    """
    def __init__(self, lines: list[str], input_dict: dict[str, Any]):
        self.lines = lines
        self.input_dict = input_dict
        self.identifiers_blocks: dict[str, CheetahBlock] = {}

    def evaluate(self) -> list[str]:
        for block in get_blocks(offset=0, lines=self.lines, indent_level=0):
            block = self.evaluate_block(block)
            self.update_lines(block)
            for child in block.child_blocks:
                child = self.evaluate_block(child)
                self.update_lines(child)
        return self.lines

    def update_lines(self, block: CheetahBlock) -> None:
        old_lines_top = self.lines[:block.real_start]
        old_lines_bottom = self.lines[block.real_stop+1:]
        self.lines = old_lines_top + block.lines + old_lines_bottom
    
    def evaluate_block(self, block: CheetahBlock) -> CheetahBlock:
        self.identifiers_blocks: dict[str, CheetahBlock] = {}
        if self.should_evaluate(block):
            template = self.prepare_template(block)
            evaluation = self.evaluate_template(template)
            if evaluation:
                self.update_block(block, evaluation)
        return block
    
    def evaluate_template(self, template: str) -> Optional[str]:
        """cheetah eval happens here"""
        try:
            t = Template(template, searchList=[self.input_dict]) # type: ignore
            print(t)
            return str(t)
        except Exception as e:
            print(e)
            return None

    def update_block(self, block: CheetahBlock, evaluation: str) -> None:
        eval_lines = utils.split_lines_blanklines(evaluation)
        eval_lines = self.expand_identifiers(eval_lines)
        block.set_lines(eval_lines) # override block contents

    def expand_identifiers(self, lines: list[str]) -> list[str]:
        out: list[str] = []
        for i in range(len(lines)):
            if self.is_uuid(lines[i]):
                block = self.identifiers_blocks[lines[i]]
                out += block.lines
                i += block.height
            else:
                i += 1
        return out

    def is_uuid(self, line: str) -> bool:
        if ' ' not in line and line in self.identifiers_blocks:
            return True
        return False

    def should_evaluate(self, block: CheetahBlock) -> bool:
        """dictates whether this block should be evaluated or left as original text"""
        permitted_blocks = [BlockType.INLINE, BlockType.CONDITIONAL]
        if block.type in permitted_blocks:
            return True
        return False

    def prepare_template(self, block: CheetahBlock) -> str:
        """
        prepares text ready for evaluation
        includes swapping child blocks with identifiers if present
        """
        template_lines = block.lines
        template_lines = self.substitute_identifiers(template_lines, block)
        template = utils.join_lines(template_lines)
        return template  # ready for evaluation
        
    def substitute_identifiers(self, template_lines: list[str], block: CheetahBlock) -> list[str]:
        for child in block.child_blocks:
            if not # TODO HERE
            self.identifiers_blocks[child.uuid] = child  # register identifier/block
            template_lines = self.substitute_identifier(template_lines, child)
        return template_lines

    def should_ignore(self, line: str) -> bool:
        if any ([line.startswith(text) for text in IGNORE_CONSTRUCTS]):
            return True
        return False

    def substitute_identifier(self, block_lines: list[str], child: CheetahBlock) -> list[str]:
        """swaps child block with identifier in template"""
        old_lines_top = block_lines[:child.relative_start]
        identifier_lines = [child.uuid] + (child.height - 1) * ['\n']
        old_lines_bottom = block_lines[child.relative_stop+1:]
        return old_lines_top + identifier_lines + old_lines_bottom



        