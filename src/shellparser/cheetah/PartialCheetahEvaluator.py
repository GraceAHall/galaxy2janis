

from __future__ import annotations
import logs.logging as logging
from typing import Any

from shellparser.cheetah.blocks import get_next_block 
from shellparser.cheetah.blocks import CheetahBlock

        
class PartialCheetahEvaluator:
    def __init__(self, lines: list[str], input_dict: dict[str, Any]):
        self.lines = lines
        self.input_dict = input_dict
        self.ptr: int = 0

    # def evaluate_multiprocess(self) -> list[str]:
    #     try:
    #         manager = multiprocessing.Manager()
    #         return_dict = manager.dict()
    #         p = multiprocessing.Process(target=self.evaluation_worker, args=(return_dict))
    #         p.start()
    #         p.join(10)
    #         if p.is_alive():
    #             logging.evaluation_failed()
    #             p.terminate()
    #             p.join()
    #         else:
    #             return return_dict['lines']  # type: ignore
    #     except Exception as e:
    #         return self.lines

    def evaluate(self) -> list[str]:
        try:
            return self.evaluation_worker()
        except Exception as e:
            return self.lines

    def evaluation_worker(self) -> list[str]:
        while self.ptr < len(self.lines):
            block = get_next_block(self.ptr, self.lines)
            block.evaluate(self.input_dict)
            self.update_lines(block)
            self.update_ptr(block)
        return self.lines

    def update_lines(self, block: CheetahBlock) -> None:
        if block.evaluated:
            old_lines_top = self.lines[:block.start]
            old_lines_bottom = self.lines[block.stop + 1:]
            self.lines = old_lines_top + block.lines + old_lines_bottom
    
    def update_ptr(self, block: CheetahBlock) -> None:
        if block.evaluated:
            self.ptr += 1  # success, go to next line
        else:
            self.ptr += block.height # TODO CHECK




