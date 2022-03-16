

from tool.tool_definition import GalaxyToolDefinition
from tool.param.InputRegister import InputRegister
from tool.param.OutputRegister import OutputRegister
from tool.TestRegister import TestRegister
from .mock_metadata import MOCK_METADATA


MOCK_TOOL = GalaxyToolDefinition(
    metadata=MOCK_METADATA,
    command='',
    inputs=InputRegister([]),
    outputs=OutputRegister([]),
    tests=TestRegister([])
)