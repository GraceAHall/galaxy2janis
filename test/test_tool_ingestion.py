

import unittest
from data.tool_args import error_tools, passing_tools


from gxtool2janis import load_galaxy_manager, load_tool
from runtime.startup import load_settings
from runtime.settings import ExecutionSettings

from tool.tool_definition import GalaxyToolDefinition
from tool.metadata import Metadata
from tool.requirements import CondaRequirement

from tool.param.InputRegister import InputRegister
from tool.param.InputParam import DataParam, FloatParam, SelectParam

from tool.param.OutputRegister import OutputRegister
from tool.param.OutputParam import DataOutputParam

from janis_core.tool.test_classes import (
    TTestCase, 
    TTestExpectedOutput, 
    TTestPreprocessor
)
from tool.test import TestRegister


class TestGalaxyIngestion(unittest.TestCase):
    """
    tests loading of tool XML.
    Ensures xml is loaded correctly into internal representation (GalaxyToolDefinition).
    """

    def setUp(self) -> None:
        args: list[str] = passing_tools['abricate']
        esettings: ExecutionSettings = load_settings(args)
        self.gxmanager = load_galaxy_manager(esettings)
        self.tool = load_tool(self.gxmanager)

    def test_tool(self) -> None:
        self.assertIsNotNone(self.tool)
        self.assertIsInstance(self.tool, GalaxyToolDefinition)

    def test_all_tools(self) -> None:
        for toolname, args in passing_tools.items():
            esettings: ExecutionSettings = load_settings(args)
            gxmanager = load_galaxy_manager(esettings)
            tool = load_tool(gxmanager)
            self.assertIsNotNone(tool)

    def test_metadata(self) -> None:
        tool = self.tool
        self.assertIsInstance(tool.metadata, Metadata)
        self.assertEquals(tool.metadata.id, 'abricate')
        self.assertEquals(tool.metadata.name, 'ABRicate')
        self.assertEquals(tool.metadata.version, '1.0.1')
        self.assertEquals(tool.metadata.description, 'Mass screening of contigs for antimicrobial and virulence genes')
        self.assertIsNone(tool.metadata.creator)
    
    def test_requirements(self) -> None:
        tool= self.tool
        self.assertIsInstance(tool.requirements[0], CondaRequirement)
        self.assertEquals(len(tool.requirements), 1)
        req: CondaRequirement = tool.requirements[0] #type: ignore
        self.assertEquals(req.name, 'abricate')
        self.assertEquals(req.version, '1.0.1')
    
    def test_inputs(self) -> None:
        tool = self.tool
        self.assertIsInstance(tool.inputs, InputRegister)
        self.assertEquals(len(tool.get_inputs()), 5)

    def test_input_params(self) -> None:
        tool = self.tool
        param = tool.get_input('file_input')
        self.assertIsNotNone(param)
        self.assertIsInstance(param, DataParam)
        self.assertEquals(param.name, 'file_input') #type: ignore
        self.assertEquals(param.datatypes, ['fasta', 'genbank', 'embl']) #type: ignore

        param = tool.get_input('adv.db')
        self.assertIsNotNone(param)
        self.assertIsInstance(param, SelectParam)

        param = tool.get_input('adv.min_dna_id')
        self.assertIsNotNone(param)
        self.assertIsInstance(param, FloatParam)
        param = tool.get_input('adv.min_dna_id')
        self.assertIsNotNone(param)
        self.assertIsInstance(param, FloatParam)
        
    def test_outputs(self) -> None:
        tool = self.tool
        self.assertIsInstance(tool.outputs, OutputRegister)
        self.assertEquals(len(tool.list_outputs()), 1)
        
        param = tool.get_output('report')
        self.assertIsNotNone(param)
        self.assertIsInstance(param, DataOutputParam)
        self.assertEquals(param.datatypes, ['tabular']) #type: ignore

    @unittest.skip("TTestCase parsing currently disabled")
    def test_tests(self) -> None:
        """checks tool xml <tests> ingestion"""
        # All tests are being loaded into register
        tool = self.tool
        self.assertIsInstance(tool.tests, TestRegister)
        self.assertEquals(len(tool.list_tests()), 8)

        # TTestCase properly created for galaxy test case 
        test = tool.list_tests()[0]
        self.assertIsNotNone(test)
        self.assertIsInstance(test, TTestCase)

        # TTestCase inputs
        # TODO add more here later
        self.assertEquals(test.input['file_input'], 'Acetobacter.fna')
        
        # TTestCase outputs
        # Test-1
        test = tool.list_tests()[0]
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
        test = tool.list_tests()[1]
        ttestout = test.output[0]
        self.assertEqual(ttestout.preprocessor, TTestPreprocessor.FileContent)
        self.assertEqual(ttestout.expected_file, 'output_mrsa.txt')




        