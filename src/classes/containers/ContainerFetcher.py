

from typing import Union, Tuple, Optional


import requests
import json
import os
from Bio import pairwise2
import regex as re

from classes.Logger import Logger


class ContainerFetcher:
    def __init__(self, tool_id: str, tool_version: str, requirements: list[dict[str, Union[str, int]]], logger: Logger) -> None:
        self.tool_id = tool_id
        self.tool_version = tool_version
        self.requirements = requirements
        self.logger = logger
        self.main_requirement = None
        self.container_cache = None
        self.container_cache_path = 'container_cache/cache.json' 
        self.container_url = None
        self.container_status = 'ok'


    def fetch(self):
        self.identify_main_requirement()
        self.load_container_cache()
        self.set_container()
        return self.container_url, self.container_status, self.main_requirement["version"]


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
                req['aln_score'] = self.global_align(self.tool_id, req['name']) # type: ignore
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
            self.container_cache = json.load(fp)

    
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

        container_url = ''
  
        if self.url_is_cached(self.tool_id, self.tool_version):
            container_url = self.container_cache[self.tool_id][self.tool_version]

        else:
            if self.main_requirement['type'] == 'package':
                container_url = self.get_container_url_by_package()

            elif self.main_requirement['type'] == 'container':
                container_url = self.get_container_url_by_container()

            self.update_container_cache(container_url)
        
        self.container_url = container_url
        

    def get_container_url_by_package(self) -> str:
        # get data package from api request
        request_url = f'https://api.biocontainers.pro/ga4gh/trs/v2/tools?name={self.main_requirement["name"]}&limit=10&sort_field=id&sort_order=asc'
        tool_data_list = self.make_api_request(request_url)
        
        # choose the most similar tool in package
        tool_data = self.get_most_similar_tool(self.main_requirement["name"], tool_data_list)

        # get the api url for the chosen tool + version
        version_url = self.get_tool_version_url(tool_data, self.tool_version)
        
        # get the images of the specific tool + version
        images_data = self.make_api_request(version_url)

        # select the biocontainers image
        biocontainer_image_url = self.get_biocontainer_image_url(images_data)

        return biocontainer_image_url


    def make_api_request(self,  request_url: str) -> dict:
        # make request to get information about tools with similar name
        try:
            response = requests.get(request_url, timeout=5)
        except requests.exceptions.Timeout:
            response = None

        # if failed, retry. max 5 times. 
        iterations = 1
        while response is None:
            if iterations > 5:
                break
            try:
                response = requests.get(request_url, timeout=5)
            except requests.exceptions.Timeout:
                response = None
            iterations += 1

        if response.status_code != 200:
            self.logger.log(2, f'no container found for {request_url}')

        else:
            data = json.loads(response.text)
            return data


    def get_most_similar_tool(self, target_name: str, api_results: dict) -> dict:
        result_similarities = []
        for tool in api_results:
            score = self.global_align(tool['name'], target_name)
            result_similarities.append((score, tool))

        result_similarities.sort(key = lambda x: x[0], reverse=True)
        return result_similarities[0][1]


    def get_tool_version_url(self, tool_data: dict, target_version: str) -> str:
        # try to get exact version
        image_versions = [v['meta_version'] for v in tool_data['versions']]
        chosen_version = ''

        # try perfect matches first        
        chosen_version = self.get_version_from_vanilla(image_versions, target_version)

        # try again removing nondigits from target_version and meta_versions
        if chosen_version == '':
            target_version = self.strip_to_numeric_version(target_version)
            image_versions = self.trim_versions(image_versions)
            chosen_version = self.get_version_from_trimmed(image_versions, target_version)

        # try again if failed but just select the most similar numerically
        if chosen_version == '':
            chosen_version = self.get_version_from_trimmed_inexact(image_versions, target_version)

        # actually get the chosen version url
        if chosen_version != '':
            for version in tool_data['versions']:
                if version['meta_version'] == chosen_version:
                    return version['url']

        self.logger.log(2, 'could not find tool version in api request')
        

    def get_version_from_vanilla(self, exact_versions: list[str], target_version: str) -> str:
        for meta_version in exact_versions:
            if meta_version == target_version:
                self.container_status = 'ok'
                return meta_version
        return ''


    def strip_to_numeric_version(self, the_string: str) -> str:
        pattern = r'(\d+)(\.\d+)+'
        matches = re.finditer(pattern, the_string)
        matches = [m[0] for m in matches]
        if len(matches) == 0:
            print()
        return matches[0]


    def trim_versions(self, image_versions: list[str]) -> str:
        """
        trims any nondigits from meta_version, then chooses an exact trimmed verion
        match if exists to target_version. target_version is also trimmed.
        """
        out_versions = []

        # trimming
        for meta_version in image_versions:
            trans_version = self.strip_to_numeric_version(meta_version)
            out_versions.append([meta_version, trans_version])
        
        out_versions.sort()
        return out_versions

    
    def get_version_from_trimmed(self, image_versions: list[str], target_version: str) -> str:
        """
        version matching to trimmed version numbers
        """
        for meta_version, trans_version in image_versions:
            if trans_version == target_version:
                self.container_status = 'nonidentical version name'
                return meta_version

        return ''


    def get_version_from_trimmed_inexact(self, image_versions: list[str], target_version: str) -> str:
        """
        try again if failed but just select the most similar numerically
        process:
            set up the version as num array,
            compare to target version (as num array),
            numeric sorts once all versions have been compared 
        """
        version_comparisons = []
        array_size = self.get_version_array_size(target_version, image_versions)

        for meta_version, trans_version in image_versions:
            v_comparison_array = self.get_version_comparison(trans_version, target_version, array_size)
            version_comparisons.append([meta_version, trans_version, v_comparison_array])

        self.container_status = 'version mismatch'
        return self.get_most_similar_version(version_comparisons)

        
    def get_version_array_size(self, target_version: str, versions: list[str]) -> int:
        max_array_size = len(target_version.split('.'))
        for _, trans_version in versions:
            max_array_size = max(max_array_size, len(trans_version.split('.')))
        return max_array_size


    def get_version_comparison(self, trans_version: str, target_version: str, array_size: int) -> Tuple:
        target_array = target_version.split('.')
        trans_array = trans_version.split('.')
        target_array = [int(digit) for digit in target_array]
        trans_array = [int(digit) for digit in trans_array]

        # standardise array size
        while len(target_array) < array_size:
            target_array.append(0)
        while len(trans_array) < array_size:
            trans_array.append(0)

        # calc discrepancies per number
        out_array = []
        for target_num, trans_num in zip(target_array, trans_array):
            out_array.append(abs(target_num - trans_num))
        
        return out_array


    def get_most_similar_version(self, version_comparisons: list) -> str:       
        # this looks really strange but works
        # since python default sort is stable, sorts version num array
        # from end to start. creates the intended sort behaviour. 
        for i in range(len(version_comparisons[0][2])):
            version_comparisons.sort(key=lambda x: x[2][-i])

        return version_comparisons[0][0]


    def get_biocontainer_image_url(self, images_data: dict) -> str:
        # get images of correct version
        version_level_images = []
        for image in images_data['images']:
            if image['registry_host'] == 'quay.io/':
                version_level_images.append(image)

        if len(version_level_images) == 0:
            self.logger.log(2, 'could not find quayio image for tool version')
        
        # get the most recent image build of that version
        images_dates = []
        for image in version_level_images:
            date_val = int(image['updated'].replace('-', '')[:8])
            images_dates.append((date_val, image))

        images_dates.sort(key = lambda x: x[0], reverse=True)
        return images_dates[0][1]['image_name']
        
        
    def get_container_url_by_container(self) -> str:
        self.logger.log(0, 'container requirement encountered')
        container_url = 'quay.io/biocontainers/' + self.main_requirement['name']
        return container_url


    def url_is_cached(self, tool_id: str, tool_version: str) -> bool:
        # does the tool_id exist in cache?
        try:
            cache_url = self.container_cache[tool_id][tool_version]
            if cache_url:
                return True
        except KeyError:
            return False


    def update_container_cache(self, container_url: str) -> None:
        # create dict for tool_id if needed
        if self.tool_id not in self.container_cache:
            self.container_cache[self.tool_id] = {}

        # set the container url for that version
        if self.tool_version not in self.container_cache[self.tool_id]:
            self.container_cache[self.tool_id][self.tool_version] = container_url
            
        # write cache to file
        with open(self.container_cache_path, 'w') as fp:
            json.dump(self.container_cache, fp)
        
