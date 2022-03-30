

import unittest

from startup.ExeSettings import WorkflowExeSettings
from workflows.workflow.WorkflowFactory import WorkflowFactory

from mock.mock_esettings import MOCK_WORKFLOW_ESETTINGS

class TestWorkflow(unittest.TestCase):
    """tests whether a Workflow() is correctly generated"""

    def setUp(self) -> None:
        esettings: WorkflowExeSettings = MOCK_WORKFLOW_ESETTINGS
        factory: WorkflowFactory = WorkflowFactory()
        self.workflow = factory.create(
            workflow_path=esettings.get_galaxy_workflow_path()
        )

    def test_metadata(self) -> None:
        metadata = self.workflow.metadata
        self.assertEquals(metadata.name, 'Unicycler training (imported from uploaded file)')
        self.assertEquals(metadata.annotation, 'Unicycler Assembly')
        self.assertEquals(metadata.tags, ['assembly'])
        self.assertEquals(metadata.version, 1)

    def test_steps(self) -> None:
        pass
    
    def test_connections(self) -> None:
        pass
    
    def test_workflow_inputs(self) -> None:
        pass

    def test_workflow_outputs(self) -> None:
        pass
