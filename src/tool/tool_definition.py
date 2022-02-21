


from dataclasses import dataclass
from typing import Any, Optional

from tool.metadata import Metadata
from tool.param.Param import Param
from tool.param.InputRegister import InputRegister
from tool.param.OutputRegister import OutputRegister
from tool.TestRegister import TestRegister
from janis_core.tool.test_classes import TTestCase
from tool.requirements import ContainerRequirement, CondaRequirement

Requirement = ContainerRequirement | CondaRequirement



@dataclass
class GalaxyToolDefinition:
    """
    High-level component representing a tool. 
    Does not depend on lower level representations or parsing.
    Permits storing and retreiving data about the tool.
    """
    metadata: Metadata
    command: str
    inputs: InputRegister
    outputs: OutputRegister
    tests: TestRegister
    

    def get_input(self, query: str, strategy: str='default') -> Optional[Param]:
        return self.inputs.get(query.lstrip('$'), strategy=strategy)
    
    def get_inputs(self, format: str='list') -> Any:
        if format == 'list':
            return self.inputs.list()
        elif format == 'dict':
            return self.inputs.to_dict()

    def get_output(self, query: str, strategy: str='default') -> Optional[Param]:
        return self.outputs.get(query.lstrip('$'), strategy=strategy)
    
    def list_outputs(self) -> list[Param]:
        return self.outputs.list()

    def list_tests(self) -> list[TTestCase]:
        return self.tests.list()

    def get_requirements(self) -> list[Requirement]:
        return self.metadata.requirements
    
    def get_main_requirement(self) -> Requirement:
        return self.metadata.get_main_requirement()













