



from typing import Any

from runtime.settings.ExeSettings import ToolExeSettings
from .expand import expand_tool_state
from .flatten import get_flattened_tool_state
from .resolve import resolve_values
from .standardisation import standardise_tool_state


# MODULE ENTRY
def load_tool_state(esettings: ToolExeSettings, step: dict[str, Any]) -> dict[str, Any]:
    step['tool_state'] = expand_tool_state(step)
    step['tool_state'] = get_flattened_tool_state(step)
    step['tool_state'] = resolve_values(esettings, step)
    step['tool_state'] = standardise_tool_state(step)
    return step['tool_state']

