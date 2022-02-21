

from tool.tool_definition import GalaxyToolDefinition

class XMLCommandLoader:
    """loads <command> section from xml file"""
    
    def __init__(self, tooldef: GalaxyToolDefinition):
        self.tooldef = tooldef

    def load(self) -> str:
        return self.tooldef.command
       




        
    
    
    
    