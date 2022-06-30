
from dataclasses import dataclass
from typing import Any, Optional

from gx.wrappers import Wrapper


@dataclass
class StepMetadata:
    wrapper: Wrapper
    uuid: str
    step_id: int
    step_name: str
    tool_state: dict[str, Any]
    workflow_outputs: list[dict[str, Any]]
    label: Optional[str] = None

