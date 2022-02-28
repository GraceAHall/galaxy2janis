






from dataclasses import dataclass
from typing import Any





@dataclass
class WorkflowOutput:
    pass


def parse_output(details: dict[str, Any]) -> WorkflowOutput:
    pass