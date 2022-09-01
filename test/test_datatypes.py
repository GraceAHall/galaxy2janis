

import unittest
from galaxy2janis import datatypes
from galaxy2janis.datatypes.core import file_t, string_t, bool_t

# mock objects
from mock.mock_components import MOCK_POSITIONAL1
from mock.mock_components import MOCK_FLAG1
from mock.mock_components import MOCK_OPTION2
from mock.mock_components import MOCK_REDIRECT_OUTPUT
from mock.mock_entities import MOCK_WORKFLOW_INPUT1


class TestDatatypeInference(unittest.TestCase):
    """
    tests the datatype which is assigned to an entity
    """
    def setUp(self) -> None:
        datatypes.populate()

    def test_positional(self) -> None:
        self.assertEquals(datatypes.get(MOCK_POSITIONAL1), file_t)
    
    def test_flag(self) -> None:
        self.assertEquals(datatypes.get(MOCK_FLAG1), bool_t)
    
    def test_option(self) -> None:
        self.assertEquals(datatypes.get(MOCK_OPTION2), string_t)
    
    def test_outputs(self) -> None:
        self.assertEquals(datatypes.get(MOCK_REDIRECT_OUTPUT), file_t)
    
    def test_workflow_input(self) -> None:
        self.assertEquals(datatypes.get(MOCK_WORKFLOW_INPUT1), file_t)
    
    # def test_option_typestring(self) -> None:
    #     raise NotImplementedError()



