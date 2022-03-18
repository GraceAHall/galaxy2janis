


from typing import Any, Optional
import requests
from requests import Response
import json


class GA4CHInteractor:

    def search(self, toolname: Optional[str]=None, version: Optional[dict[str, str]]=None) -> Any:
        if toolname:
            return self.request_tool_data(toolname)
        elif version:
            return self.request_tool_version_data(version)
        else:
            raise RuntimeError()

    def request_tool_data(self, tool_query: str) -> Optional[list[dict[str, Any]]]:
        """
        make api request which returns dict of search results
        select the correct tool from results & return
        """
        api_uri = self.format_tool_request_url(tool_query)
        results = self.make_api_request(api_uri)
        return self.handle_response(results)

    def format_tool_request_url(self, tool_query: str) -> str:
        return f'https://api.biocontainers.pro/ga4gh/trs/v2/tools?name={tool_query}&limit=10&sort_field=id&sort_order=asc'
    
    def make_api_request(self, request_url: str) -> Optional[Response]:
        # make requests to get information about tools with similar name
        iterations = 1
        response: Optional[Response] = None
        while response is None:
            if iterations > 5:
                break
            try:
                response = requests.get(request_url, timeout=5)
            except requests.exceptions.Timeout:
                response = None
            iterations += 1
        return response

    def handle_response(self, response: Optional[Response]) -> Optional[list[dict[str, Any]]]:
        if response and response.status_code != 200:
            print(f'WARN: no GA4GH response')
        else:
            return json.loads(response.text)

    def request_tool_version_data(self, version: dict[str, str]) -> Optional[list[dict[str, Any]]]:
        api_uri = version['url']
        results = self.make_api_request(api_uri)
        return self.handle_response(results)