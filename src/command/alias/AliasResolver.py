

from tool.tool_definition import GalaxyToolDefinition

class AliasResolver:
    def __init__(self, tool: GalaxyToolDefinition):
        self.tool = tool
    
    def resolve(self, the_string: str) -> str:
        pass