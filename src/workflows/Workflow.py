

import json
from typing import Any 

from .Step import WorkflowStep, parse_step
from .Input import WorkflowInput, parse_input
from .Output import WorkflowOutput, parse_output



class Workflow:
    """should this have some sort of tree structure?"""

    def __init__(self, workflow_path: str):
        self.tree = self.load_tree(workflow_path)
        self.steps: dict[str, WorkflowStep] = self.parse_steps()
        #self.inputs: dict[str, WorkflowInput] = self.parse_inputs()
        #self.outputs: dict[str, WorkflowOutput] = self.parse_outputs()

    def load_tree(self, path: str) -> dict[str, Any]:
        with open(path, 'r') as fp:
            return json.load(fp)

    def parse_steps(self) -> dict[str, WorkflowStep]:
        # TODO should probably check the workflow type (.ga, .ga2)
        # and internal format is valid
        out: dict[str, WorkflowStep] = {}
        
        for stepnum, details in self.tree['steps'].items():
            out[stepnum] = parse_step(details)
        return out

    def parse_inputs(self) -> dict[str, WorkflowInput]:
        raise NotImplementedError
    
    def parse_outputs(self) -> dict[str, WorkflowOutput]:
        raise NotImplementedError


    



