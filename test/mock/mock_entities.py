

from entities.workflow import WorkflowInput
from datatypes.core import file_t

MOCK_WORKFLOW_INPUT1 = WorkflowInput(
    name='inFastq1',
    array=False,
    optional=False,
    is_runtime=False,
    datatype=file_t,
    value=None
)