


from dataclasses import dataclass
from typing import Any, Optional

from tool.metadata import Metadata
from tool.requirements import Requirement
from tool.param.InputRegister import InputRegister
from tool.param.OutputRegister import OutputRegister
from tool.test import TestRegister
from janis_core.tool.test_classes import TTestCase
from tool.param.Param import Param


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

    def inputs_to_json(self) -> dict[str, Any]:
        return self.inputs.to_json()













