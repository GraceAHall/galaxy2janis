

from xmltool.XMLToolDefinition import XMLToolDefinition

class XMLCommandLoader:
    """loads <command> section from xml file"""
    
    def __init__(self, tooldef: XMLToolDefinition):
        self.tooldef = tooldef

    def load(self) -> str:
        return self.tooldef.raw_command
       




        
    
    
    
    