

import unittest

from startup.ExeSettings import WorkflowExeSettings
from workflows.workflow.WorkflowInteractor import WorkflowInteractor

from mock.mock_esettings import MOCK_WORKFLOW_ESETTINGS

class TestWorkflow(unittest.TestCase):
    """tests whether a Workflow() is correctly generated"""

    def setUp(self) -> None:
        self.esettings: WorkflowExeSettings = MOCK_WORKFLOW_ESETTINGS
        self.interactor: WorkflowInteractor = WorkflowInteractor()
        self.interactor.load_workflow(self.esettings.get_workflow_path())

    def test_metadata(self) -> None:
        metadata = self.interactor.get_metadata()
        self.assertEquals(metadata.name, 'Unicycler training (imported from uploaded file)')
        self.assertEquals(metadata.annotation, 'Unicycler Assembly')
        self.assertEquals(metadata.format_version, '0.1')
        self.assertEquals(metadata.tags, ['assembly'])
        self.assertEquals(metadata.uuid, '4599788d-06f9-4733-bd98-95918b92b5bd')
        self.assertEquals(metadata.version, 1)

    def test_steps(self) -> None:
        pass
    
    def test_connections(self) -> None:
        pass
    
    def test_workflow_inputs(self) -> None:
        pass

    def test_workflow_outputs(self) -> None:
        pass
