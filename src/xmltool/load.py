

from runtime.ExeSettings import ToolExeSettings
from galaxy_interaction import GalaxyManager
from xmltool.XMLToolDefinition import XMLToolDefinition
from xmltool.parsing.GalaxyToolIngestor import GalaxyToolIngestor


def load_xmltool(esettings: ToolExeSettings) -> XMLToolDefinition:
    gxmanager = GalaxyManager(esettings)
    galaxytool = gxmanager.get_tool()
    ingestor = GalaxyToolIngestor(galaxytool)
    return XMLToolDefinition(
        ingestor.get_metadata(),
        ingestor.get_command(),
        ingestor.get_inputs(),
        ingestor.get_outputs(),
        ingestor.get_tests()
    )
