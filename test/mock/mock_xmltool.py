

from xmltool.tool_definition import XMLToolDefinition
from xmltool.param.InputParamRegister import InputParamRegister
from xmltool.param.OutputParamRegister import OutputParamRegister
from xmltool.TestRegister import TestRegister
from .mock_metadata import MOCK_METADATA


MOCK_XMLTOOL = XMLToolDefinition(
    metadata=MOCK_METADATA,
    raw_command='',
    inputs=InputParamRegister([]),
    outputs=OutputParamRegister([]),
    tests=TestRegister([])
)