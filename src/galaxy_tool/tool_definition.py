


from dataclasses import dataclass
from typing import Optional

from galaxy_tool.metadata import Metadata
from galaxy_tool.requirements import Requirement
from galaxy_tool.param.InputRegister import InputRegister
from galaxy_tool.param.OutputRegister import OutputRegister
from galaxy_tool.test import TestRegister
from janis_core.tool.test_classes import TTestCase
from galaxy_tool.param.Param import Param


@dataclass
class GalaxyToolDefinition:
    """
    High-level component representing a tool. 
    Does not depend on lower level representations or parsing.
    Permits storing and retreiving data about the tool.
    """
    metadata: Metadata
    requirements: list[Requirement]
    command: str
    inputs: InputRegister
    outputs: OutputRegister
    tests: TestRegister

    def get_input(self, query: str, strategy: str='default') -> Optional[Param]:
        return self.inputs.get(query, strategy=strategy)
    
    def get_output(self, query: str, strategy: str='default') -> Optional[Param]:
        return self.outputs.get(query, strategy=strategy)

    def list_inputs(self) -> list[Param]:
        return self.inputs.list()
    
    def list_outputs(self) -> list[Param]:
        return self.outputs.list()

    def list_tests(self) -> list[TTestCase]:
        return self.tests.list()













