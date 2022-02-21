



from dataclasses import dataclass
from typing import Optional, Tuple

from tool.citations import Citation
from command.cmdstr.utils import global_align
from tool.requirements import ContainerRequirement, CondaRequirement

Requirement = ContainerRequirement | CondaRequirement

@dataclass
class Metadata:
    name: str
    id: str
    version: str
    description: str
    help: str
    requirements: list[Requirement]
    citations: list[Citation]
    creator: Optional[str]

    def get_main_requirement(self) -> Requirement:
        """
        sets the main tool requirement
        if no requirements parsed, sets to tool info
        else, sets from the parsed requirements. 
        method:
            - align each requirement to the tool id
            - pick the one with best alignment score
        """
        if len(self.requirements) == 0:
            return CondaRequirement(self.id, self.version)
        
        similarity_scores = self.get_req_similarity_scores()
        similarity_scores.sort(key=lambda x: x[1], reverse=True)
        main_requirement: Requirement = similarity_scores[0][0]
        return main_requirement

    def get_req_similarity_scores(self) -> list[Tuple[Requirement, float]]:
        scores: list[Tuple[Requirement, float]] = []
        for req in self.requirements:
            similarity = global_align(req.get_text(), self.id)
            scores.append((req, similarity))
        return scores
             
    def get_main_citation(self) -> str:
        raise NotImplementedError()

    def get_main_citation_old(self) -> str:
        # TODO UPDATE THIS WITH CitationManager galaxy source
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