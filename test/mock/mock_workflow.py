


from galaxy2janis.entities.workflow import Workflow

from mock.mock_metadata import MOCK_WORKFLOW_METADATA
from mock.mock_entities import MOCK_WORKFLOW_INPUT1
from mock.mock_entities import MOCK_STEP1


MOCK_WORKFLOW = Workflow()
MOCK_WORKFLOW.set_metadata(MOCK_WORKFLOW_METADATA)
MOCK_WORKFLOW.add_input(MOCK_WORKFLOW_INPUT1)
MOCK_WORKFLOW.add_step(MOCK_STEP1)
