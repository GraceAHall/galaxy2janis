
from typing import Any
from command.cheetah.PartialCheetahEvaluator import PartialCheetahEvaluator
import command.text.simplification.utils as utils


def sectional_evaluate(text: str, inputs: dict[str, Any]) -> str:
    raw_lines = utils.split_lines_blanklines(text)
    evaluator = PartialCheetahEvaluator(raw_lines, inputs)
    eval_lines = evaluator.evaluate()
    return utils.join_lines(eval_lines)