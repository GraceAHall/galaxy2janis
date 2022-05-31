
import requests
from bs4 import BeautifulSoup, Tag
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class StepMetadata:
    uuid: str
    step_id: int
    step_name: str
    tool_id: str
    tool_state: dict[str, Any]
    is_inbuilt: bool
    workflow_outputs: list[dict[str, Any]]
    repo_name: Optional[str] = None
    label: Optional[str] = None
    owner: Optional[str] = None
    changeset_revision: Optional[str] = None
    shed: Optional[str] = None
    tool_definition_path: Optional[str] = None

    def get_url(self) -> str:
        try: 
            return self.get_url_via_version()
        except Exception as e:
            print(e)
            assert(self.changeset_revision)
            return self.get_url_via_revision(self.changeset_revision)

    def get_url_via_revision(self, changeset_revision: str) -> str:
        return f'https://{self.shed}/repos/{self.owner}/{self.repo_name}/archive/{changeset_revision}.tar.gz'
    
    # a method which uses version instead of build
    # takes time unless data is cached
    def get_url_via_version(self) -> str:
        assert(self.owner)
        assert(self.repo_name)
        interactor = ToolShedInteractor(self.owner, self.repo_name)
        revisions = interactor.get_revisions()
        revs_versions: dict[str, str] = {}
        for revision in revisions:
            revs_versions[revision] = interactor.get_revision_version(revision)
        print()


class ToolShedInteractor:
    def __init__(self, owner: str, tool: str):
        self.owner = owner
        self.tool = tool

    def get_repo_url(self) -> str:
        return f'https://toolshed.g2.bx.psu.edu/view/{self.owner}/{self.tool}/'
    
    def get_iframe_url(self, iframe_elem: Tag) -> str:
        return f'https://toolshed.g2.bx.psu.edu/{iframe_elem.attrs["src"]}'
    
    def get_revision_url(self, revision: str) -> str:
        return f'https://toolshed.g2.bx.psu.edu/view/{self.owner}/{self.tool}/{revision}'
    
    def get_soup(self, url: str) -> BeautifulSoup:
        response = requests.get(url)
        return BeautifulSoup(response.content, "html.parser")

    def get_revisions(self) -> list[str]:
        page_url = self.get_repo_url()
        page = self.get_soup(page_url)
        iframe = self.load_iframe(page)
        return self.scrape_revision_options(iframe)

    def scrape_revision_options(self, iframe: BeautifulSoup) -> list[str]:
        changeset_elem = iframe.find(id='change_revision')
        options = changeset_elem.find_all('option') # type: ignore
        return [opt.attrs['value'] for opt in options] # type: ignore

    def load_iframe(self, page: BeautifulSoup) -> BeautifulSoup:
        iframe_elem = page.find('iframe')
        iframe_url = self.get_iframe_url(iframe_elem) # type: ignore
        return self.get_soup(iframe_url)

    def get_revision_version(self, revision: str) -> str:
        url = self.get_revision_url(revision)
        page = self.get_soup(url)
        iframe = self.load_iframe(page)
        return self.scrape_tool_version(iframe)

    def scrape_tool_version(self, iframe: BeautifulSoup) -> str:
        changeset_elem = iframe.find(id='valid_tools')
        rows = changeset_elem.find_all('tr') # type: ignore
        assert(len(rows) == 3) # type: ignore
        row = rows[-1] # type: ignore
        cols = changeset_elem.find_all('td') # type: ignore
        assert(len(cols) == 5) # type: ignore
        return cols[3].contents[0] # type: ignore


        



