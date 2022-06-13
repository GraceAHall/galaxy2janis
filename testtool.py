


from janis_core import (
    CommandToolBuilder, 
    String,
    Directory,
    ToolInput, 
    ToolOutput,
    WildcardSelector
)


tool1 = CommandToolBuilder(
    tool="tool1",
    version="0.1",
    container="quay.io/biocontainers/python:3.10",
    base_command=['echo'],
    inputs=myinputs,
    outputs=[
        ToolOutput(
            'workdir',
            Directory,
            selector=WildcardSelector("."),
	    )
    ]
)

myinputs = [
    ToolInput(
        'text',
        String,
        default='hello!',
        position=1,
    )
],