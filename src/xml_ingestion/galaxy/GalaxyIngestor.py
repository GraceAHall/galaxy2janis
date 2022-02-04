

from galaxy.tools import Tool as GalaxyToolRepresentation

from xml_ingestion.galaxy.GalaxyToolLoader import GalaxyToolLoader
from xml_ingestion.galaxy.InputParamFactory import InputParamFactory
from xml_ingestion.galaxy.OutputParamFactory import OutputParamFactory

from galaxy_tool.param.InputRegister import InputRegister
from galaxy_tool.param.OutputRegister import OutputRegister
from galaxy_tool.test import TestRegister
from xml_ingestion.galaxy.TestFactory import TestFactory
from galaxy_tool.requirements import Requirement, CondaRequirement, ContainerRequirement
from galaxy_tool.metadata import Metadata

import galaxy_utils




class GalaxyIngestor:
    def __init__(self, xml_path: str):
        self.toolrep: GalaxyToolRepresentation = self.load_xml(xml_path)

    def load_xml(self, xml_path: str) -> GalaxyToolRepresentation:
        loader = GalaxyToolLoader()
        return loader.load(xml_path)

    def get_metadata(self) -> Metadata:
        """returns a formatted Metadata using the representation"""
        return Metadata(
            name = str(self.toolrep.name),  #type: ignore
            id = str(self.toolrep.id),  #type: ignore
            version = str(self.toolrep.version).split('+galaxy')[0],  #type: ignore
            description = str(self.toolrep.description),  #type: ignore
            help = str(self.toolrep.raw_help),  #type: ignore
            citations = [],
            creator = self.toolrep.creator  #type: ignore
        )
    
    def get_requirements(self) -> list[Requirement]:
        """returns a formatted list of Requirements using the representation"""
        reqs: list[Requirement] = []
        reqs += self.get_conda_requirements()
        reqs += self.get_container_requirements()
        return reqs
    
    def get_conda_requirements(self) -> list[CondaRequirement]:
        packages: list[dict[str, str]] = self.toolrep.requirements.to_list() # type: ignore
        return [CondaRequirement(p['name'], p['version']) for p in packages]

    def get_container_requirements(self) -> list[ContainerRequirement]:
        containers: list[ContainerDescription] = self.toolrep.containers # type: ignore
        return [ContainerRequirement(c.identifier) for c in containers] # type: ignore

    def get_command(self) -> str:
        """returns the tool xml command"""
        return str(self.toolrep.command) # type: ignore
    
    def get_inputs(self) -> InputRegister:
        """returns a an InputRegister by reformatting the galaxy tool representation's params."""
        gx_params = galaxy_utils.get_flattened_params(self.toolrep)
        fac = InputParamFactory()
        inputs = [fac.produce(gxp) for gxp in gx_params]
        return InputRegister(inputs)
    
    def get_outputs(self) -> OutputRegister:
        """returns a formatted list of outputs using the representation"""
        fac = OutputParamFactory()
        outputs = [fac.produce(gxp) for gxp in self.toolrep.outputs.values()]
        return OutputRegister(outputs)
    
    def get_tests(self) -> TestRegister:
        """returns a formatted list of tests using the representation"""
        fac = TestFactory()
        ttestcases = [fac.produce(t) for t in self.toolrep.tests]
        return TestRegister(ttestcases)
