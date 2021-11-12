

from typing import Union, Tuple, Optional


import requests
import json
import os




class ContainerFetcher:
    def __init__(self, tool_id: str, tool_version: str, requirements: list[dict[str, Union[str, int]]]) -> None:
        self.tool_id = tool_id
        self.tool_version = tool_version
        self.requirements = requirements
        self.main_requirement = None
        self.container_cache = None


    def fetch(self):
        self.identify_main_requirement()
        self.load_container_cache()
        self.set_container()


    def identify_main_requirement(self) -> None:
        """
        sets the main tool requirement

        if no requirements parsed, sets to tool info
        else, sets from the parsed requirements. method:
            align each requirement to the tool id
            pick the one with best alignment score
        """
        if len(self.requirements) == 0:
            self.main_requirement = {'type': 'package', 'version': self.tool_version, 'name': self.tool_id, 'aln_score': 0}

        else:
            for req in self.requirements:
                req['aln_score'] = self.global_align(self.tool_name, req['id']) # type: ignore
                #req['aln_score'] = self.global_align(self.tool_name, req['name']) # type: ignore
            
            self.requirements.sort(key=lambda x: x['aln_score'], reverse=True)
            self.main_requirement = self.requirements[0]


    def global_align(self, pattern: str, template: str) -> int:
        pattern = pattern.lower()
        template = template.lower()
        outcome = pairwise2.align.globalms(pattern, template, 2, -1, -.5, -.1) # type: ignore
        if len(outcome) > 0: # type: ignore
            score = outcome[0].score # type: ignore
        else:
            score = 0
        return score # type: ignore


    def load_container_cache(self) -> dict[str, str]:
        """
        cache structure updated to tool_id: version: container
        """
        # check file exists
        if not os.path.exists(self.container_cache_path):
            with open(self.container_cache_path, 'w') as fp:
                fp.write('{}')

        # load cache
        with open(self.container_cache_path, 'r') as fp:
            return json.load(fp)

    
    def set_container(self) -> None:
        """
        requirements have been sorted by alignment match to tool id
        the main tool requirement should be 1st in self.requirements

        container is specified differently for 'package' and 'container' requirements
        if no requirements, uses the tool id and tool version to guess a container

        once the container name and version are known, biocontainers is searched for the most recent container build which matches the name and version

        individual builds not supported, except in the case of of 'container' requirements as it just directly grabs the url from the requirement text 

        currently just templating a url then checking it exists.

        in future, want to use the api specified at https://api.biocontainers.pro/ga4gh/trs/v2/ui/ to find biocontainers. see also: https://biocontainers.pro/registry
        currently can't do this because their servers are very very slow
        """
        container_url = self.get_container_url()       

        if self.container_exists(container_url):
            self.container = container_url
            self.update_container_cache(container_url)
        else:
            self.logger.log(2, f'container could not be resolved: {container_url}')


    def get_container_url(self) -> str:
        container_url = ''
  
        if self.main_requirement['type'] == 'package':
            container_url = self.get_container_url_by_package()

        elif self.main_requirement['type'] == 'container':
            container_url = self.get_container_url_by_container()             

        return container_url


    def get_container_url_by_package(self) -> str:
        container_url = ''
        mr = self.main_requirement
        packages = self.get_bioconda_api_results('package', mr['name'], mr['version'])
        return container_url


    def get_bioconda_api_results(self, reqtype: str, name: str, version: str) -> str:
        request_url = f'https://api.biocontainers.pro/ga4gh/trs/v2/tools?name={name}&limit=10&sort_field=id&sort_order=asc'
        response = requests.get(request_url)
        print()

        if not self.container_exists(test_url):
            pass
            #test_url = base_path + f'{requirement}'

        #pattern = f'https://quay.io/biocontainers/{}'
        return pattern


    def get_container_url_by_container(self, requirement: dict[str, Union[str, int]]) -> str:
        container_url = ''
        self.logger.log(1, 'container requirement encountered')
        container_url = str(requirement['name']) 
        return container_url


    def container_exists(self, container_url: str) -> bool:
        if self.url_is_cached(container_url):
            return True
        elif self.url_exists(container_url): 
            return True
        return False


    def url_is_cached(self, container_url: str) -> bool:
        # does the tool_id exist in cache?
        if self.tool_id in self.container_cache:
            versions = self.container_cache[self.tool_id]

            # does the specific tool_version exist for that tool_id?
            if self.tool_version in versions:
                if versions[self.tool_version] == container_url:
                    return True

        return False


    def url_exists(self, container_url: str) -> bool:
        response = requests.get(container_url)
        if response.status_code == 200:
            return True
        else:
            return False


    def update_container_cache(self, container_url: str) -> None:
        if self.tool_name not in self.container_cache or self.container_cache[self.tool_name] != container_url:
            # update cache in mem
            self.container_cache[self.tool_name] = container_url
            
            # write cache to file
            with open(self.container_cache_path, 'w') as fp:
                json.dump(self.container_cache, fp)
        
