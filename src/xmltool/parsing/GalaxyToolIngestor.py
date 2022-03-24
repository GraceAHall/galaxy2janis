

from galaxy.tools import Tool as GxTool
from galaxy.tools.parameters.basic import ToolParameter as GxInput
from galaxy.tool_util.parser.output_objects import ToolOutput as GxOutput
from startup.ExeSettings import ToolExeSettings

from xmltool.metadata import ToolXMLMetadata
from xmltool.requirements import CondaRequirement, ContainerRequirement
from xmltool.citations import Citation

from xmltool.parsing.ParamFlattener import ParamFlattener
from xmltool.parsing.InputParamFactory import InputParamFactory
from xmltool.parsing.OutputParamFactory import OutputParamFactory
from xmltool.param.InputRegister import InputRegister
from xmltool.param.OutputRegister import OutputRegister

from xmltool.parsing.tests.TestFactory import TestFactory
from xmltool.TestRegister import TestRegister
from biblib.biblib import bib

Requirement = ContainerRequirement | CondaRequirement


class GalaxyToolIngestor:
    def __init__(self, gxtool: GxTool, esettings: ToolExeSettings):
        self.gxtool = gxtool
        self.esettings = esettings
        self.inputs = InputRegister([])

    def get_metadata(self, ) -> ToolXMLMetadata:
        """returns a formatted Metadata using the representation"""
        requirements: list[Requirement] = self.get_requirements()
        citations: list[Citation] = self.get_citations()
        return ToolXMLMetadata(
            name=str(self.gxtool.name),  #type: ignore
            id=str(self.gxtool.id),  #type: ignore
            version=str(self.gxtool.version).split('+galaxy')[0],  #type: ignore
            description=str(self.gxtool.description),  #type: ignore
            help=str(self.gxtool.raw_help),  #type: ignore
            requirements=requirements,
            citations=citations,
            creator=self.gxtool.creator  #type: ignore
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
        citations: list[Citation] = []
        citations += self.get_biotools_citations()
        citations += self.get_doi_citations()
        citations += self.get_bibtex_citations()
        return citations

    def get_biotools_citations(self) -> list[Citation]: 
        out: list[Citation] = []
        for ref in self.gxtool.xrefs:
            citation = Citation(
                type='biotools',
                text=f"https://bio.tools/{ref['value']}"
            )
            out.append(citation)
        return out

    def get_doi_citations(self) -> list[Citation]:
        out: list[Citation] = []
        for elem in self.gxtool.tool_source.xml_tree.findall('citations'):
            for ref in elem.findall('citation'):
                if ref.attrib['type'] == 'doi':
                    citation = Citation(
                        type='doi',
                        text=f"https://doi.org/{ref.text}"
                    )
                    out.append(citation)
        return out
        
    def get_bibtex_citations(self) -> list[Citation]:
        out: list[Citation] = []
        for elem in self.gxtool.tool_source.xml_tree.findall('citations'):
            for ref in elem.findall('citation'):
                if ref.attrib['type'] == 'bibtex':
                    citation = Citation(
                        type='bibtex',
                        text=self.parse_bibtex(ref.text)
                    )
                    out.append(citation)
        return out
    
    def parse_bibtex(self, bibtex_citation: dict[str, str]) -> str:
        # define and parse using biblib
        bp = bib.Parser()
        data = bp.parse(bibtex_citation).get_entries() # type: ignore
        # get each citation key: value pair
        entry = list(data.values())[0]  # type: ignore
        return str(entry['url']) # type: ignore

    def get_command(self) -> str:
        """returns the tool xml command"""
        return str(self.gxtool.command) # type: ignore
    
    def get_inputs(self) -> InputRegister:
        """returns a an InputRegister by reformatting the galaxy tool representation's params."""
        pf = ParamFlattener(self.gxtool.inputs)
        gx_inputs: list[GxInput] = pf.flatten()
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
