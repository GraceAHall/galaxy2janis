

from typing import Optional
import unittest
from data.tool_args import passing_tools

from startup.settings import load_tool_settings
from startup.ExeSettings import ToolExeSettings
from galaxy_interaction import load_manager, GalaxyManager
from xmltool.load import load_xmltool, XMLToolDefinition

from xmltool.metadata import Metadata
from xmltool.requirements import CondaRequirement

from xmltool.param.Param import Param
from xmltool.param.InputRegister import InputRegister
from xmltool.param.InputParam import (
    BoolParam,
    IntegerParam, 
    TextParam, 
    FloatParam,
    DataParam,
    SelectParam
)
from xmltool.param.OutputRegister import OutputRegister
from xmltool.param.OutputParam import (
    DataOutputParam,
    CollectionOutputParam 
)

from janis_core.tool.test_classes import (
    TTestCase, 
    TTestExpectedOutput, 
    TTestPreprocessor
)
from xmltool.TestRegister import TestRegister


class TestGalaxyIngestion(unittest.TestCase):
    """
    tests loading of tool XML.
    Ensures xml is loaded correctly into internal representation (XMLToolDefinition).
    """

    def setUp(self) -> None:
        args: dict[str, Optional[str]] = passing_tools['abricate']
        esettings: ToolExeSettings = load_tool_settings(args)
        self.gxmanager: GalaxyManager = load_manager(esettings)
        self.xmltool: XMLToolDefinition = load_xmltool(self.gxmanager)

    def test_tool(self) -> None:
        self.assertIsNotNone(self.xmltool)
        self.assertIsInstance(self.xmltool, XMLToolDefinition)

    def test_all_tools(self) -> None:
        for tool_args in passing_tools.values():
            esettings: ToolExeSettings = load_tool_settings(tool_args)
            gxmanager = load_manager(esettings)
            xmltool = load_xmltool(gxmanager)
            self.assertIsNotNone(xmltool)

    def test_metadata(self) -> None:
        xmltool = self.xmltool
        self.assertIsInstance(xmltool.metadata, Metadata)
        self.assertEquals(xmltool.metadata.id, 'abricate')
        self.assertEquals(xmltool.metadata.name, 'ABRicate')
        self.assertEquals(xmltool.metadata.version, '1.0.1')
        self.assertEquals(xmltool.metadata.description, 'Mass screening of contigs for antimicrobial and virulence genes')
        self.assertIsNone(xmltool.metadata.creator)
    
    def test_requirements(self) -> None:
        xmltool= self.xmltool
        requirements = xmltool.get_requirements()
        self.assertIsInstance(requirements[0], CondaRequirement)
        self.assertEquals(len(requirements), 1)
        req: CondaRequirement = requirements[0] #type: ignore
        self.assertEquals(req.name, 'abricate')
        self.assertEquals(req.version, '1.0.1')
    
    def test_inputs(self) -> None:
        xmltool = self.xmltool
        self.assertIsInstance(xmltool.inputs, InputRegister)
        self.assertEquals(len(xmltool.list_inputs()), 5)

    def test_input_params(self) -> None:
        xmltool = self.xmltool
        param = xmltool.get_input('file_input')
        self.assertIsNotNone(param)
        self.assertIsInstance(param, DataParam)
        self.assertEquals(param.name, 'file_input') #type: ignore
        self.assertEquals(param.datatypes, ['fasta', 'genbank', 'embl']) #type: ignore

        param = xmltool.get_input('adv.db')
        self.assertIsNotNone(param)
        self.assertIsInstance(param, SelectParam)

        param = xmltool.get_input('adv.min_dna_id')
        self.assertIsNotNone(param)
        self.assertIsInstance(param, FloatParam)
        param = xmltool.get_input('adv.min_dna_id')
        self.assertIsNotNone(param)
        self.assertIsInstance(param, FloatParam)
        
    def test_outputs(self) -> None:
        xmltool = self.xmltool
        self.assertIsInstance(xmltool.outputs, OutputRegister)
        self.assertEquals(len(xmltool.list_outputs()), 1)
        
        param = xmltool.get_output('report')
        self.assertIsNotNone(param)
        self.assertIsInstance(param, DataOutputParam)
        self.assertEquals(param.datatypes, ['tabular']) #type: ignore

    @unittest.skip("TTestCase parsing currently disabled")
    def test_tests(self) -> None:
        """checks tool xml <tests> ingestion"""
        # All tests are being loaded into register
        xmltool = self.xmltool
        self.assertIsInstance(xmltool.tests, TestRegister)
        self.assertEquals(len(xmltool.list_tests()), 8)

        # TTestCase properly created for galaxy test case 
        test = xmltool.list_tests()[0]
        self.assertIsNotNone(test)
        self.assertIsInstance(test, TTestCase)

        # TTestCase inputs
        # TODO add more here later
        self.assertEquals(test.input['file_input'], 'Acetobacter.fna')
        
        # TTestCase outputs
        # Test-1
        test = xmltool.list_tests()[0]
        self.assertEquals(len(test.output), 4)
        self.assertIsInstance(test.output[0], TTestExpectedOutput)
        ttestout = test.output[0]
        self.assertEqual(ttestout.preprocessor, TTestPreprocessor.LinesDiff)
        self.assertEqual(ttestout.file_diff_source, 'output_noresults.txt')
        self.assertEqual(ttestout.expected_value, 0)
        ttestout = test.output[1]
        self.assertEqual(ttestout.preprocessor, TTestPreprocessor.FileContent)
        self.assertEqual(ttestout.expected_value, 'ACCESSION')

        # Test-2
        test = xmltool.list_tests()[1]
        ttestout = test.output[0]
        self.assertEqual(ttestout.preprocessor, TTestPreprocessor.FileContent)
        self.assertEqual(ttestout.expected_file, 'output_mrsa.txt')





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




        