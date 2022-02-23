

from dataclasses import dataclass
from typing import Any, Iterable, Tuple
from runtime.settings import ToolExeSettings
import tarfile
import wget


data = {
    "tool_shed_repository": {
        "changeset_revision": "1d8fe9bc4cb0",
        "name": "fastp",
        "owner": "iuc",
        "tool_shed": "toolshed.g2.bx.psu.edu"
    },
}

f'{data["tool_shed"]}/repos/{data["owner"]}/{data["name"]}/archive/{data["changeset_revision"]}.tar.gz'


@dataclass
class ToolStepData:
    step: int
    toolname: str
    download_dir: str




class WorkflowInteractor:
    def __init__(self, esettings: ToolExeSettings):
        self.esettings = esettings
        self.workflow: dict[str, Any] = self.load_workflow()

    def load_workflow(self) -> dict[str, Any]:
        raise NotImplementedError

    def download_workflow_tools(self):
        uris = self.get_tool_uris()
        

    def get_tool_uris(self) -> dict[int, str]:
        out: dict[int, str] = {}
        for step, details in self.iter_steps():
            if details['tool_id']:
                out[step] = details['content_id']
        return out

    def download_repo(self, repo_data: dict[str, str]) -> str:
        uri = f'{data["tool_shed"]}/repos/{data["owner"]}/{data["name"]}/archive/{data["changeset_revision"]}.tar.gz'
        tarball_filename: str = wget.download(uri)
        tar = tarfile.open(tarball_filename, "r:gz")
        tar.extractall()
        tar.close()
        foldername = tarball_filename.rsplit('.tar.gz', 1)[0]
        return foldername

    def iter_steps(self) -> Iterable[Tuple[int, dict[str, Any]]]:
        steps: dict[str, Any] = self.workflow['steps']
        for step, details in steps.items():
            yield int(step), details
        
