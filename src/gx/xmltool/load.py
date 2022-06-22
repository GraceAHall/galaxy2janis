

from gx.interaction import GalaxyInteractor
from gx.xmltool.parsing.GalaxyToolIngestor import GalaxyToolIngestor
from gx.xmltool.XMLToolDefinition import XMLToolDefinition


def load_xmltool() -> XMLToolDefinition:
    gxmanager = GalaxyInteractor()  # create galaxy interactor
    galaxytool = gxmanager.get_tool()
    ingestor = GalaxyToolIngestor(galaxytool)
    return XMLToolDefinition(
        ingestor.get_metadata(),
        ingestor.get_command(),
        ingestor.get_configfiles(),
        ingestor.get_inputs(),
        ingestor.get_outputs(),
        ingestor.get_tests()
    )
