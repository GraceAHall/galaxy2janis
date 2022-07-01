


from dataclasses import dataclass
from datetime import datetime
import textwrap

from runtime.dates import JANIS_DATE_FMT
from fileio.text.TextRender import TextRender
from gx.xmltool.ToolXMLMetadata import ToolXMLMetadata


@dataclass
class ToolMetadataRender(TextRender):
    entity: ToolXMLMetadata

    def render(self) -> str:
        e = self.entity
        contributors = ['gxtool2janis']
        if e.owner:
            contributors += [f'Wrapper owner: galaxy toolshed user {e.owner}']
        if e.creator:
            contributors += [f'Wrapper creator: {e.creator}']
        return textwrap.dedent(f"""\
            metadata = ToolMetadata(
                short_documentation="{e.description}",
                keywords=[],
                contributors={contributors},
                dateCreated="{datetime.today().strftime(JANIS_DATE_FMT)}",
                dateUpdated="{datetime.today().strftime(JANIS_DATE_FMT)}",
                version="{e.version}",
                doi="{e.get_doi_citation()}",
                citation="{e.get_main_citation()}",
                documentationUrl=None,
                documentation=\"\"\"{str(e.help)}\"\"\"
            )
            """)
        
    def collect_imports(self) -> list[str]:
        return []


