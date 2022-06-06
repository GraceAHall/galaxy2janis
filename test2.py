


from janis_core.types.common_data_types import Directory

from janis_core import (
    CommandToolBuilder, 
    String,
    ToolInput, 
    ToolOutput,
    WildcardSelector
)

tool1 = CommandToolBuilder(
    tool="tool1",
    version="0.1",
    container="quay.io/biocontainers/python:3.10",
    base_command=['echo'],
    inputs=[
        ToolInput(
            'text',
            String,
            default='hello!',
            position=1,
	    )
    ],
    outputs=[
        ToolOutput(
            'workdir',
            Directory,
            selector=WildcardSelector("."),
	    )
    ]
)