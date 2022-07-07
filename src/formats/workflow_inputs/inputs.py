

from collections import defaultdict
from dataclasses import dataclass
from typing import Tuple

from entities.workflow import WorkflowInput
from entities.workflow import Workflow


@dataclass
class RuntimeInputList:
    def __init__(self, workflow: Workflow):
        self.inputs = workflow.inputs

    @property
    def formatted(self) -> list[Tuple[str, list[str]]]:
        out: list[Tuple[str, list[str]]] = []
        out.append(('input data', self.get_names(self.input_data)))
        for step_inputs in self.steps:
            out.append((self.get_step_label(step_inputs), self.get_names(step_inputs)))
        return out

    @property
    def input_data(self) -> list[WorkflowInput]:
        return [x for x in self.inputs if x.is_galaxy_input_step]
    
    @property
    def steps(self) -> list[list[WorkflowInput]]:
        the_dict: dict[int, list[WorkflowInput]] = defaultdict(list)
        for inp in self.inputs:
            if not inp.is_galaxy_input_step:
                the_dict[inp.step_id].append(inp)
        the_list = list(the_dict.items())
        the_list.sort()  # sort by step id (early steps first!)
        # return just the list of runtime values for each step in order
        return [x[1] for x in the_list] 

    def get_names(self, inputs: list[WorkflowInput]) -> list[str]:
        """translates list of workflow inputs into their underlying names"""
        return [self.tag_manager.get(inp.uuid) for inp in inputs]
    
    def get_step_label(self, inputs: list[WorkflowInput]) -> str:
        """gets the label for a step from a list of runtime inputs of that step"""
        assert(inputs)
        return f'{inputs[0].step_tag}'





