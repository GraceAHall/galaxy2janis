

import unittest
from execution import load_settings
from tool.param.OutputParam import DataOutputParam
from xml_ingestion import ingest

from tool.tool_definition import GalaxyToolDefinition
from tool.metadata import Metadata
from tool.requirements import CondaRequirement
from tool.param.InputRegister import InputRegister
from tool.param.OutputRegister import OutputRegister
#from tool.test import TestRegister

from tool.param.InputParam import DataParam, FloatParam, SelectParam

class TestIngestion(unittest.TestCase):
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


