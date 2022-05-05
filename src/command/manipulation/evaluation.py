
from typing import Any
from command.cheetah.SectionalCheetahEvaluator import SectionalCheetahEvaluator
import command.manipulation.utils as utils


def sectional_template(text: str, inputs: dict[str, Any]) -> str:
    raw_lines = utils.split_lines_blanklines(text)
    evaluator = SectionalCheetahEvaluator(raw_lines, inputs)
    eval_lines = evaluator.evaluate()
    return utils.join_lines(eval_lines)