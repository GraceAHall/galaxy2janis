

from gx.gxtool.param.OutputParam import OutputParam
import logs.logging as logging

from galaxy.tools import Tool as GxTool
from galaxy.tools.parameters.basic import ToolParameter
from galaxy.tool_util.parser.output_objects import ToolOutput

from gx.configfiles.Configfile import Configfile
from gx.gxtool.ToolXMLMetadata import ToolXMLMetadata
from gx.gxtool.citations import Citation
from gx.gxtool.param.Param import Param
from gx.gxtool.parsing.ParamFlattener import ParamFlattener
from gx.gxtool.param.InputParamRegister import InputParamRegister
from gx.gxtool.param.OutputParamRegister import OutputParamRegister
from gx.gxtool.TestRegister import TestRegister
from gx.gxtool.requirements import CondaRequirement, ContainerRequirement
Requirement = ContainerRequirement | CondaRequirement

from .outputs import parse_output_param
from .inputs import parse_input_param


class GalaxyToolIngestor:
    def __init__(self, gxtool: GxTool):
        self.gxtool = gxtool
        self.inputs = InputParamRegister([])

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
        #citations += self.get_bibtex_citations()
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
        if 'url' in entry:
            return f"{entry['url']}" # type: ignore
        elif 'author' in entry and 'title' in entry:
            return f"{entry['author']}.  {entry['title']}"
        return ''

    def get_command(self) -> str:
        """returns the tool xml command"""
        return str(self.gxtool.command) # type: ignore
    
    def get_configfiles(self) -> list[Configfile]:
        """returns the tool configfiles"""
        out: list[Configfile] = []
        for name, _, contents in self.gxtool.config_files:  # type: ignore
            if isinstance(contents, str):
                new_config = Configfile(name, contents)  # type: ignore
                out.append(new_config)
        if out:
            logging.has_configfile()
        return out
    
    def get_inputs(self) -> InputParamRegister:
        """returns a an InputRegister by reformatting the galaxy tool representation's params."""
        g_in_params = self.flatten_params()
        inputs: list[Param] = []
        for g_param in g_in_params:
            t_param = parse_input_param(g_param)
            inputs.append(t_param)
        register = InputParamRegister(inputs)
        self.inputs = register
        return register

    def flatten_params(self) -> list[ToolParameter]:
        pf = ParamFlattener(self.gxtool.inputs)
        return pf.flatten()

    def get_outputs(self) -> OutputParamRegister:
        """returns a formatted list of outputs using the representation"""
        g_out_params: list[ToolOutput] = list(self.gxtool.outputs.values())
        outputs: list[OutputParam] = []
        for g_param in g_out_params:
            t_param = parse_output_param(g_param, self.inputs)
            outputs.append(t_param)
        return OutputParamRegister(outputs)
    
    def get_tests(self) -> TestRegister:
        """
        returns a formatted list of tests using the representation
        needs to be properly fleshed out later!
        """
        return TestRegister([])
