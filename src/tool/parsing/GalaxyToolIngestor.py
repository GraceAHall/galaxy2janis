

from galaxy.tools import Tool as GxTool
from galaxy.tools.parameters.basic import ToolParameter as GxInput
from galaxy.tool_util.parser.output_objects import ToolOutput as GxOutput

from tool.metadata import Metadata
from tool.requirements import CondaRequirement, ContainerRequirement
from tool.citations import Citation

from tool.parsing.InputParamFactory import InputParamFactory
from tool.parsing.OutputParamFactory import OutputParamFactory
from tool.param.InputRegister import InputRegister
from tool.param.OutputRegister import OutputRegister

from tool.parsing.tests.TestFactory import TestFactory
from tool.TestRegister import TestRegister

from tool.parsing.inputs import get_flattened_params

Requirement = ContainerRequirement | CondaRequirement


class GalaxyToolIngestor:
    def __init__(self, gxtool: GxTool):
        self.gxtool = gxtool
        self.inputs = InputRegister([])

    def get_metadata(self) -> Metadata:
        """returns a formatted Metadata using the representation"""
        requirements: list[Requirement] = self.get_requirements()
        citations: list[Citation] = self.get_citations()
        return Metadata(
            name = str(self.gxtool.name),  #type: ignore
            id = str(self.gxtool.id),  #type: ignore
            version = str(self.gxtool.version).split('+galaxy')[0],  #type: ignore
            description = str(self.gxtool.description),  #type: ignore
            help = str(self.gxtool.raw_help),  #type: ignore
            requirements = requirements,
            citations = citations,
            creator = self.gxtool.creator  #type: ignore
        )
    
    def get_requirements(self) -> list[Requirement]:
        """returns a formatted list of Requirements using the representation"""
        reqs: list[Requirement] = []
        reqs += self.get_conda_requirements()
        reqs += self.get_container_requirements()
        return reqs
    
    def get_conda_requirements(self) -> list[CondaRequirement]:
        packages: list[dict[str, str]] = self.gxtool.requirements.to_list() # type: ignore
        return [CondaRequirement(p['name'], p['version']) for p in packages]

    def get_container_requirements(self) -> list[ContainerRequirement]:
        containers: list[ContainerDescription] = self.gxtool.containers # type: ignore
        return [ContainerRequirement(c.identifier) for c in containers] # type: ignore

    def get_citations(self) -> list[Citation]:
        return []

    def get_command(self) -> str:
        """returns the tool xml command"""
        return str(self.gxtool.command) # type: ignore
    
    def get_inputs(self) -> InputRegister:
        """returns a an InputRegister by reformatting the galaxy tool representation's params."""
        gx_inputs: list[GxInput] = get_flattened_params(self.gxtool)
        fac = InputParamFactory()
        inputs = [fac.produce(gxp) for gxp in gx_inputs]
        # caching the input register for use in getting outputs
        self.inputs = InputRegister(inputs)
        return self.inputs
    
    def get_outputs(self) -> OutputRegister:
        """returns a formatted list of outputs using the representation"""
        fac = OutputParamFactory()
        gx_outputs: list[GxOutput] = list(self.gxtool.outputs.values())
        outputs = [fac.produce(gxp, self.inputs) for gxp in gx_outputs]
        return OutputRegister(outputs)
    
    def get_tests(self) -> TestRegister:
        """
        returns a formatted list of tests using the representation
        needs to be properly fleshed out later!
        """
        return TestRegister([])
        #fac = TestFactory()
        #ttestcases = [fac.produce(t) for t in self.gxtool.tests]
        #return TestRegister(ttestcases)
