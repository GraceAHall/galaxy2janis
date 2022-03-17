

from typing import Any
import json

from .Step import WorkflowStep
from .StepParsingStrategy import StepParsingStrategy, InputDataStepParsingStrategy, ToolStepParsingStrategy


### parsing galaxy to steps -----------
def parse_step(step: dict[str, Any]) -> WorkflowStep:
    strategy = select_strategy(step)
    return strategy.parse(step)

def select_strategy(step: dict[str, Any]) -> StepParsingStrategy:
    # there may be a step['type'] = 'parameter_input' too but I haven't seen it yet
    step['tool_state'] = json.loads(step['tool_state'])
    if step['type'] in ['data_input', 'data_collection_input']:
        return InputDataStepParsingStrategy()
    return ToolStepParsingStrategy()



    


