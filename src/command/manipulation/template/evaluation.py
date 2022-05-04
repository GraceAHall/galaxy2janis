


from __future__ import annotations
from typing import Any, Optional
import command.manipulation.utils as utils
from command.manipulation.template.blocks import CheetahBlock


def sectional_template(text: str, inputs: dict[str, Any]) -> str:
    evaluator = SectionalCheetahEvaluator(inputs)
    main_block = CheetahBlock(
        line_start=0, 
        line_stop=0,
        lines=utils.split_lines(text)
    )
    main_block = evaluator.evaluate(main_block)
    return utils.join_lines(main_block.lines)


    
class SectionalCheetahEvaluator:
    """
    evaluates a cheetah template with a supplied input_dict.
    returns the output str, or None if fails
    recursive
    """
    def __init__(self, input_dict: dict[str, Any]):
        self.input_dict = input_dict
        self.block_register: dict[str, CheetahBlock] = {} 

    def evaluate(self, block: CheetahBlock) -> CheetahBlock:
        self.refresh_attributes()
        if self.should_evaluate():
            template = self.prepare_template(block)
            evaluation = self.evaluate_template(template)
            
            if evaluation:
                block.set_lines(evaluation) # override block contents
                for child in block.child_blocks:
                    child = self.evaluate(child) # evaluate child blocks 
                    block.replace_child_block(child) # swap in eval child lines
        return block 
    
    def refresh_attributes(self) -> None:
        """resets attrs so a new block can be evaluated"""
        self.block_register: dict[str, CheetahBlock] = {} 

    def should_evaluate(self) -> bool:
        """dictates whether this block should be evaluated or left as original text"""
        raise NotImplementedError()

    def prepare_template(self, block: CheetahBlock) -> str:
        """
        prepares text ready for evaluation
        includes swapping child blocks with identifiers if present
        """
        template = self.substitute_identifiers(block)
        template = utils.join_lines(block.lines)
        return template  # ready for evaluation
        
    def substitute_identifiers(self, block: CheetahBlock) -> str:
        for block in block.child_blocks:  # TODO HERE
            self.block_register[block.uuid] = block  # register identifier/block
            template = self.substitute_identifier(template, block) # update template
        return template

    def substitute_identifier(self, template: str, block: CheetahBlock) -> str:
        """swaps child block with identifier in template"""
        raise NotImplementedError()

    def evaluate_template(self, template: str) -> Optional[list[str]]:
        """cheetah eval happens here"""
        raise NotImplementedError()
    



    # def update_block(self, evaluation: Optional[str]) -> None:
    #     """
    #     updates block text with evaluation
    #     restores block contents if identifier present
    #     """
    #     if evaluation:
    #         pass
    #     raise NotImplementedError()