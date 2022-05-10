


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







"""
#if str( $paired_unpaired.fastq_input_selector ) == "paired"
    #if $paired_unpaired.fastq_input1.is_of_type('fastqsanger')
        #set fq1 = "fq1.fastq"
    #elif $paired_unpaired.fastq_input1.is_of_type('fastqsanger.gz')
        #set fq1 = "fq1.fastq.gz"
    #end if
    #if $paired_unpaired.fastq_input2.is_of_type('fastqsanger')
        #set fq2 = "fq2.fastq"
    #elif $paired_unpaired.fastq_input2.is_of_type('fastqsanger.gz')
        #set fq2 = "fq2.fastq.gz"
    #end if
    ln -s '${paired_unpaired.fastq_input1}' $fq1 &&
    ln -s '${paired_unpaired.fastq_input2}' $fq2 &&
#elif str( $paired_unpaired.fastq_input_selector ) == "paired_collection"
    #if $paired_unpaired.fastq_input1.forward.is_of_type('fastqsanger')
        #set fq1 = "fq1.fastq"
    #elif $paired_unpaired.fastq_input1.forward.is_of_type('fastqsanger.gz')
        #set fq1 = "fq1.fastq.gz"
    #end if
    #if $paired_unpaired.fastq_input1.reverse.is_of_type('fastqsanger')
        #set fq2 = "fq2.fastq"
    #elif $paired_unpaired.fastq_input1.reverse.is_of_type('fastqsanger.gz')
        #set fq2 = "fq2.fastq.gz"
    #end if
    ln -s '${paired_unpaired.fastq_input1.forward}' $fq1 &&
    ln -s '${paired_unpaired.fastq_input1.reverse}' $fq2 &&
#elif str( $paired_unpaired.fastq_input_selector ) == "single"
    #if $paired_unpaired.fastq_input1.is_of_type('fastqsanger')
        #set fq = "fq.fastq"
    #elif $paired_unpaired.fastq_input1.is_of_type('fastqsanger.gz')
        #set fq = "fq.fastq.gz"
    #end if
    ln -s '${paired_unpaired.fastq_input1}' '$fq' &&
#end if
"""






# class SectionalCheetahEvaluatorOld:
#     """
#     evaluates a cheetah template with a supplied input_dict.
#     returns the output str, or None if fails
#     recursive
#     """
#     def __init__(self, lines: list[str], input_dict: dict[str, Any]):
#         self.lines = lines   # the <command> section text to alter
#         self.input_dict = input_dict
#         self.masked_blocks: dict[str, CheetahBlock] = {}

#     def evaluate(self) -> list[str]:
#         for block in get_blocks(offset=0, lines=self.lines, indent_level=0):
#             self.evaluate_block(block)
#         return self.lines

#     def evaluate_block(self, block: CheetahBlock) -> None:
#         self.identifiers_blocks: dict[str, CheetahBlock] = {}
#         if self.should_evaluate(block):
#             template = self.prepare_template(block)
#             print('\ntemplate:')
#             print(template)
#             evaluation = self.evaluate_template(template)
#             print('\nevaluation:')
#             print(evaluation)
#             if evaluation is not None:
#                 self.update_block(block, evaluation)
#                 self.update_lines(block)
#                 for child in block.child_blocks:
#                     self.evaluate_block(child)


#     def evaluate_template(self, source: str) -> Optional[str]:
#         """cheetah eval happens here"""
#         try:
#             t = Template(source, searchList=[self.input_dict]) 
#             return unicodify(t)
#         except Exception as e:
#             print('\n' + str(e))
#             return None

#     def update_block(self, block: CheetahBlock, evaluation: str) -> None:
#         eval_lines = utils.split_lines_blanklines(evaluation)
#         eval_lines = self.expand_identifiers(eval_lines)
#         block.lines = eval_lines # override block contents

#     def update_lines(self, block: CheetahBlock) -> None:
#         old_lines_top = self.lines[:block.real_start]
#         old_lines_bottom = self.lines[block.real_stop+1:]
#         self.lines = old_lines_top + block.lines + old_lines_bottom



        