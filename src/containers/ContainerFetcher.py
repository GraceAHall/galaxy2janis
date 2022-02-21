

from dataclasses import dataclass
from typing import Any, Optional
from containers.GA4GHInteractor import GA4CHInteractor
from containers.VersionMatcher import VersionMatcher
from utils.general_utils import global_align

from tool.tool_definition import GalaxyToolDefinition
from containers.Container import Container
from tool.requirements import ContainerRequirement, CondaRequirement


Requirement = ContainerRequirement | CondaRequirement

@dataclass
class SimilarityScore:
    score: float
    obj: Any


class ContainerFetcher:
    """
    container is specified differently for 'package' and 'container' requirements
    if no requirements, uses the tool id and tool version to guess a container
    
    main 'tool' requirement is guessed in a Metadata() instance on the Tool() class
    
    ga4gh is searched for the most recent container build which matches the name and version

    individual builds not supported, except in the case of of 'container' requirements as it just directly grabs the url from the requirement text 
    """
    def __init__(self, tool: GalaxyToolDefinition) -> None:
        self.tool = tool
        self.requirement = tool.metadata.get_main_requirement()
        self.ga4gh_interactor = GA4CHInteractor()
        self.version_matcher = VersionMatcher()

    def fetch(self) -> Optional[Container]:
        match self.requirement:
            case CondaRequirement():
                return self.get_biocontainer_by_package()
            case ContainerRequirement():
                return self.get_biocontainer_by_container()
            case _:
                raise RuntimeError()

    def get_biocontainer_by_package(self) -> Optional[Container]:
        # get tool information from api request
        query_name = self.requirement.get_text()
        results = self.ga4gh_interactor.search(tool=query_name)
        
        if results:
            tool_data = self.select_most_similar_tool(results)
            version = self.select_most_similar_version(tool_data)
            tool_version_data = self.ga4gh_interactor.search(version=version)

            if tool_version_data:
                image = self.select_image(tool_version_data)
                return Container(
                    tool=self.tool.metadata.id,
                    version=self.tool.metadata.version,
                    url=image['image_name'],
                    image_type=image['image_type'],
                    registry_host=image['registry_host'],
                )
        return None
    
    def select_most_similar_tool(self, api_results: list[dict[str, Any]]) -> dict[str, Any]:
        """returns data for the api tool result most similar to the query tool name"""
        result_similarities: list[SimilarityScore] = []
        query_name = self.requirement.get_text()
        for tool in api_results:
            score = global_align(query_name, tool['name'])
            result_similarities.append(SimilarityScore(score, tool))
        result_similarities.sort(key = lambda x: x.score, reverse=True)
        return result_similarities[0].obj

    def select_most_similar_version(self, tool_data: dict[str, Any]) -> dict[str, str]:
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

    def select_image(self, data: dict[str, Any]) -> dict[str, str]:
        images = [x for x in data['images'] if x['image_type'] != 'Conda']
        for image in images:
            if image['registry_host'] == 'quay.io/':
                return image
        for image in images:
            if image['registry_host'] == 'depot.galaxyproject.org/singularity/':
                return image
        return images[0]

    def get_biocontainer_by_container(self) -> Optional[Container]:
        raise NotImplementedError()
        

