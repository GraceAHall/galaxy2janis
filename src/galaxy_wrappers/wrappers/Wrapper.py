
from datetime import datetime


from runtime.settings.formats import JANIS_DATE_FMT


class Wrapper:
    def __init__(self, details: dict[str, str]):
        self.owner: str = details['owner']
        self.repo: str = details['repo']
        self.revision: str = details['revision']
        self.tool_id: str = details['tool_id']
        self.tool_version: str = details['tool_version']
        self.date_created: datetime = datetime.strptime(details['date_created'], JANIS_DATE_FMT)
        self.inbuilt: bool = False
        
    @property
    def tool_build(self) -> str:
        return self.tool_version.split('+galaxy')[0]
    
    @property
    def url(self) -> str:
        return f'https://toolshed.g2.bx.psu.edu/repos/{self.owner}/{self.repo}/archive/{self.revision}.tar.gz'

    def to_dict(self) -> dict[str, str]:
        return {
            'owner': self.owner,
            'repo': self.repo,
            'revision': self.revision,
            'tool_id': self.tool_id,
            'tool_version': self.tool_version,
            'tool_build': self.tool_build,
            'date_created': self.date_created.strftime(JANIS_DATE_FMT),
            'url': self.url,
        }
