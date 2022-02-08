

import unittest

from tool.param.Param import Param


from tool.param.OutputRegister import OutputRegister
from tool.param.OutputParam import (
    DataOutputParam,
    CollectionOutputParam
)

from tool.param.InputRegister import InputRegister
from tool.param.InputParam import (
    BoolParam,
    IntegerParam, 
    TextParam, 
    FloatParam,
    DataParam
)


class TestInputRegister(unittest.TestCase):
    """
    tests the ParamRegister code
    this is kinda bad because it mutates register then asserts register length
    """
    def setUp(self) -> None:
        inputs: list[Param] = [
            TextParam('param1'),
            IntegerParam('section1.param1'),
            FloatParam('section1.param2'),
            DataParam('section2.param1'),
            BoolParam('section2.param2')
        ]
        self.register = InputRegister(inputs)

    def test_list(self) -> None:
        self.assertEquals(len(self.register.list()), 5)

    def test_get_default(self) -> None:
        param = self.register.get('param1', strategy='default')
        self.assertIsNotNone(param)
        if param:
            self.assertEquals(param.name, 'param1')
    
    def test_get_lca1(self) -> None:
        param = self.register.get('section2.param1', strategy='lca')
        self.assertIsNotNone(param)
        if param:
            self.assertEquals(param.name, 'section2.param1')
    
    def test_get_lca2(self) -> None:
        param = self.register.get('param1', strategy='lca')
        self.assertIsNotNone(param)
        if param:
            self.assertEquals(param.name, 'param1')



class TestOutputRegister(unittest.TestCase):
    """
    tests the ParamRegister code
    this is kinda bad because it mutates register then asserts register length
    """
    def setUp(self) -> None:
        inputs: list[Param] = [
            DataOutputParam('param1'),
            CollectionOutputParam('param2'),
        ]
        self.register = OutputRegister(inputs)

    def test_list(self) -> None:
        self.assertEquals(len(self.register.list()), 2)
    
    def test_get_filepath(self) -> None:
        self.assertRaises(NotImplementedError)
    

    
class TestTestRegister(unittest.TestCase):
    """for the TestRegister class"""
    pass


