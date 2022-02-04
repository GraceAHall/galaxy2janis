

from typing import Any
import unittest

from execution import load_settings
from xml_ingestion import ingest

from galaxy_tool.tool_definition import GalaxyToolDefinition
from galaxy_tool.metadata import Metadata
from galaxy_tool.requirements import CondaRequirement

from galaxy_tool.param.InputRegister import InputRegister
from galaxy_tool.param.InputParam import DataParam, FloatParam, SelectParam

from galaxy_tool.param.OutputRegister import OutputRegister
from galaxy_tool.param.OutputParam import DataOutputParam

from janis_core.tool.test_classes import TTestCase
from galaxy_tool.test import TestRegister


class TestGalaxyIngestion(unittest.TestCase):
    """
    tests loading of tool XML.
    Ensures xml is loaded correctly into internal representation (GalaxyToolDefinition).
    """

    def setUp(self) -> None:
        argv = [
            "abricate.xml", "test/data/abricate", 
            "--outdir", "test/rubbish",
        ]
        esettings = load_settings(argv)
        self.tool = ingest(esettings.get_xml_path(), method='galaxy')

    def test_tool(self) -> None:
        self.assertIsNotNone(self.tool)
        self.assertIsInstance(self.tool, GalaxyToolDefinition)

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
        self.assertEquals(len(tool.list_inputs()), 5)

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
        self.assertIsInstance(test.input, dict[str, Any])
        self.assertEquals(test.input['file_input'], 'Acetobacter.fna')
        
        # TTestCase outputs
        self.assertIsInstance(test.output, list[TTestExpectedOutput])
        #self.assertEquals(test.input[0], )
        TTestExpectedOutput(
                        "out_variants_gridss",
                        preprocessor=TTestPreprocessor.FileContent,
                        operator=operator.eq,
                        expected_file=f"{chr17}/NA12878/brca1.germline.gridss.vcf",
                    ),



        