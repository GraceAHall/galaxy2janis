





"""
adjust main step to have an output of type: Directory, perhaps with an outputBinding: { glob: . }, then add the corresponding type: Directory input to post-step
"""

from janis_core.types.common_data_types import Directory
from janis_core import WorkflowBuilder


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
tool2 = CommandToolBuilder(
    tool="tool2",
    version="0.1",
    container="quay.io/biocontainers/python:3.10",
    base_command=['echo'],
    inputs=[
        ToolInput(
            'workdir',
            Directory,
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

w = WorkflowBuilder("my_workflow")
w.step(
    'step1',
    tool1(
        text='hihi!'
    )
)
w.step(
    'step2',
    tool2(
        workdir=w.step1.workdir,
    )
)

w.output(
	"out_step1_workdir",
	Directory,
	source=(w.step1, "workdir")
)
w.output(
	"out_step2_workdir",
	Directory,
	source=(w.step2, "workdir")
)



