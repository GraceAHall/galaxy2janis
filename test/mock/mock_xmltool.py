

from xmltool.tool_definition import XMLToolDefinition
from xmltool.param.InputRegister import InputRegister
from xmltool.param.OutputRegister import OutputRegister
from xmltool.TestRegister import TestRegister
from .mock_metadata import MOCK_METADATA


MOCK_XMLTOOL = XMLToolDefinition(
    metadata=MOCK_METADATA,
    command='',
    inputs=InputRegister([]),
    outputs=OutputRegister([]),
    tests=TestRegister([])
)