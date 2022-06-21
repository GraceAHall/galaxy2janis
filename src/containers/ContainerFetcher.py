


import runtime.logging.logging as logging
from abc import ABC, abstractmethod
from datetime import datetime
from dataclasses import dataclass
from typing import Any, Optional

from utils.general_utils import global_align
from xmltool.requirements import Requirement

from .GA4GHInteractor import GA4GHInteractor
from .VersionMatcher import VersionMatcher
from .Container import Container


image_presets = {
    'python': {
        'image_name': 'https://hub.docker.com/_/ubuntu',
        'image_type': 'Docker',
        'registry_host': 'hub.docker.com/'
    }
}


class BiocontainerFetcher(ABC):
    """
    ga4gh is searched for the most recent container build which matches the name and version

    individual builds not supported, except in the case of of 'container' requirements as it just directly grabs the url from the requirement text 
    """
    def __init__(self) -> None:
        self.ga4gh_interactor = GA4GHInteractor()
        self.version_matcher = VersionMatcher()

    @abstractmethod
    def fetch(self, tool_id: str, tool_version: str, requirement: Requirement) -> Optional[Container]:
        """finds a relevant biocontainer for a given tool requirement"""
        ...


class ContainerBiocontainerFetcher(BiocontainerFetcher):
    
    def fetch(self, tool_id: str, tool_version: str, requirement: Requirement) -> Optional[Container]:
        return Container(
            galaxy_id=tool_id,
            galaxy_version=tool_version,
            url=requirement.get_text(),
            image_type=requirement.get_type(),
            registry_host=requirement.get_text().split('/', 1)[0]
        )




@dataclass
class SimilarityScore:
    score: float
    obj: Any


 
# class GA4GHVersionData:
#     def __init__(self, **kwargs: dict[str, str]):
#         self.image_name = kwargs['image_name']
#         self.image_type = kwargs['image_type']
#         self.image_type = kwargs['image_type']


class CondaBiocontainerFetcher(BiocontainerFetcher):

    def fetch(self, tool_id: str, tool_version: str, requirement: Requirement) -> Optional[Container]:
        # get tool information from api request
        self.set_attributes(tool_id, tool_version, requirement)
       
        image = self.get_image_preset()
        if not image:
            image = self.get_image_GA4GH()
            if image:
                return Container(
                    galaxy_id=self.tool_id,
                    galaxy_version=self.tool_version,
                    url=image['image_name'],
                    image_type=image['image_type'],
                    registry_host=image['registry_host'],
                    requirement_id=self.requirement.get_text(),
                    requirement_version=self.requirement.get_version()
                )
        return None

    def get_image_preset(self) -> Optional[dict[str, str]]:
        name = self.requirement.get_text()
        if name in image_presets:
            return image_presets[name]
        return None
            
    def get_image_GA4GH(self) -> Optional[dict[str, str]]:
        name = self.requirement.get_text()
        api_results = self.ga4gh_interactor.search(toolname=name)
        if api_results:
            tool_version_data = self.get_tool_version_data(api_results)
            if tool_version_data:
                return self.select_image(tool_version_data)
        return None

    def set_attributes(self, tool_id: str, tool_version: str, requirement: Requirement) -> None:
        self.tool_id = tool_id
        self.tool_version = tool_version
        self.requirement = requirement

    def get_tool_version_data(self, api_results: list[dict[str, Any]]) -> Optional[dict[str, Any]]:
        tool_data = self.select_most_similar_tool(api_results)
        version = self.select_most_similar_version(tool_data)
        return self.ga4gh_interactor.search(version=version)
    
    def select_most_similar_tool(self, api_results: list[dict[str, Any]]) -> dict[str, Any]:
        """returns data for the api tool result most similar to the query tool name"""
        result_similarities: list[SimilarityScore] = []
        query_name = self.requirement.get_text()
        for tool_data in api_results:
            score = global_align(query_name, tool_data['name'])
            result_similarities.append(SimilarityScore(score, tool_data))
        result_similarities.sort(key = lambda x: x.score, reverse=True)
        return result_similarities[0].obj

    def select_most_similar_version(self, tool_data: dict[str, Any]) -> dict[str, Any]:
        vm = self.version_matcher
        target_version = self.requirement.get_version()
        selected: Optional[dict[str, str]] = None

        selected = vm.get_version_exact(tool_data, target_version)
        if not selected:
            selected = vm.get_version_trimmed(tool_data, target_version)
        if not selected:
            selected = vm.get_most_recent(tool_data)
        return selected
        # if not selected:
        #     selected = vm.get_version_trimmed_inexact(query_versions, target_version)

    def select_image(self, data: dict[str, Any]) -> dict[str, Any]:
        images = self.sort_dates(data['images'])
        if not images:
            logging.no_container()
        selected = self.select_from_available(images)
        if selected:
            return selected
        else:
            logging.container_version_mismatch()
            return images[0] 

    def select_from_available(self, images: list[dict[str, Any]]) -> Optional[dict[str, Any]]:
        for image in images:
            if image['registry_host'] == 'quay.io/':
                return image
        for image in images:
            if image['registry_host'] == 'depot.galaxyproject.org/singularity/':
                return image
        return None

    def sort_dates(self, images: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(images, key=lambda x: datetime.strptime(x['updated'], "%Y-%m-%dT%H:%M:%SZ"), reverse=True)


        

