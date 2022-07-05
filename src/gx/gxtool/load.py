

from gx.interaction import get_tool

from gx.gxtool.parsing.GalaxyToolIngestor import GalaxyToolIngestor
from gx.gxtool.XMLToolDefinition import XMLToolDefinition

import settings


def load_xmltool() -> XMLToolDefinition:
    gxtool = get_tool(settings.tool.tool_path)
    ingestor = GalaxyToolIngestor(gxtool)
    return XMLToolDefinition(
        ingestor.get_metadata(),
        ingestor.get_command(),
        ingestor.get_configfiles(),
        ingestor.get_inputs(),
        ingestor.get_outputs(),
        ingestor.get_tests()
    )
