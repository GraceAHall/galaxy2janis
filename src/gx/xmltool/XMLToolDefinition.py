


from dataclasses import dataclass
from typing import Optional

from gx.xmltool.ToolXMLMetadata import ToolXMLMetadata
from gx.xmltool.param.OutputParam import OutputParam
from gx.xmltool.param.Param import Param
from gx.xmltool.param.InputParamRegister import InputParamRegister
from gx.xmltool.param.OutputParamRegister import OutputParamRegister
from gx.xmltool.TestRegister import TestRegister
from janis_core.tool.test_classes import TTestCase
from gx.xmltool.requirements import ContainerRequirement, CondaRequirement

Requirement = ContainerRequirement | CondaRequirement



@dataclass
class XMLToolDefinition:
    """
    High-level component representing a tool. 
    Does not depend on lower level representations or parsing.
    Permits storing and retreiving data about the tool.
    """
    metadata: ToolXMLMetadata
    raw_command: str
    configfiles: dict[str, str]
    inputs: InputParamRegister
    outputs: OutputParamRegister
    tests: TestRegister

    def get_input(self, query: str, strategy: str='exact') -> Optional[Param]:
        return self.inputs.get(query.lstrip('$'), strategy=strategy)
    
    def list_inputs(self) -> list[Param]:
        return self.inputs.list()

    def get_output(self, query: str, strategy: str='exact') -> Optional[Param]:
        return self.outputs.get(query.lstrip('$'), strategy=strategy)
    
    def list_outputs(self) -> list[OutputParam]:
        return self.outputs.list()

    def list_tests(self) -> list[TTestCase]:
        return self.tests.list()

    def get_requirements(self) -> list[Requirement]:
        return self.metadata.requirements
    
    def get_main_requirement(self) -> Requirement:
        return self.metadata.get_main_requirement()













