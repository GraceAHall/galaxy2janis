


from galaxy_interaction import GalaxyManager
from tool.tool_definition import GalaxyToolDefinition
from tool.parsing.tool_ingest import parse_gx_to_internal


def load_tool(gxmanager: GalaxyManager) -> GalaxyToolDefinition:
    galaxytool = gxmanager.get_tool()
    return parse_gx_to_internal(galaxytool)