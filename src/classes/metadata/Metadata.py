

#pyright: basic

from xml.etree import ElementTree as et
from typing import Union
from biblib.biblib import bib
from utils.general_utils import global_align

from galaxy.tools import Tool as GalaxyTool
from classes.logging.Logger import Logger
from utils.etree_utils import get_attribute_value


class Metadata:
    def __init__(self, gxtool: GalaxyTool) -> None:
        self.name: str = gxtool.name
        self.id: str = gxtool.id
        self.version: str = gxtool.version
        self.creator: str = gxtool.creator
        self.description: str = gxtool.description
        self.requirements: list[dict[str, Union[str, int]]] = self.get_requirements(gxtool)
        self.main_requirement: dict[str, Union[str, int]] = self.get_main_requirement()
        self.citations: list[dict[str, str]] = self.get_citations(gxtool)
        self.help: str = gxtool.raw_help
    

    def get_requirements(self, gxtool: GalaxyTool) -> list[dict]:
        reqs = gxtool.requirements.to_list()
        for req in reqs:
            req['aln_score'] = 0
        return reqs


    def get_main_requirement(self) -> None:
        """
        sets the main tool requirement

        if no requirements parsed, sets to tool info
        else, sets from the parsed requirements. method:
            align each requirement to the tool id
            pick the one with best alignment score
        """
        if len(self.requirements) == 0:
            return {'type': 'package', 'version': self.tool.version, 'name': self.id, 'aln_score': 0}

        else:
            for req in self.requirements:
                req['aln_score'] = global_align(self.id, req['name']) # type: ignore
            
            self.requirements.sort(key=lambda x: x['aln_score'], reverse=True)
            return self.requirements[0]
             

    def get_citations(self, gxtool: GalaxyTool) -> list[dict[str, str]]:
        return []


    # TODO UPDATE THIS WITH CitationManager galaxy source
    def get_main_citation(self) -> str:
        doi_citations = [c for c in self.citations if c['type'] == 'doi']
        if len(doi_citations) > 0:
            doi_citation = doi_citations[0]
            return str(doi_citation['text'])
        
        bibtex_citations = [c for c in self.citations if c['type'] == 'bibtex']
        if len(bibtex_citations) > 0:
            bibtex_citation = self.parse_bibtex(bibtex_citations[0])
            return str(bibtex_citation) 
        
        else:
            return 'tool xml missing citation'
    

    def parse_bibtex(self, bibtex_citation: dict[str, str]) -> str:
        # define and parse using biblib
        bp = bib.Parser()
        data = bp.parse(bibtex_citation['text'], log_fp=sys.stderr).get_entries() # type: ignore

        # get the key: value pairs
        entry = list(data.values())[0]  # type: ignore
        return str(entry['url']) # type: ignore





 
