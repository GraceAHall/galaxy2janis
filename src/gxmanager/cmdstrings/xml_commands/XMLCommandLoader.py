

from tool.tool_definition import GalaxyToolDefinition

class XMLCommandLoader:
    """
    loads and processes xml command section
    the raw xml command string is processed into a more usable state
    aim is to remove constructs like cheetah comments, conditional lines without
    removing other elements like #set directives which will be used later. 

    some stdio stuff is managed here. '| tee ', '|& tee ', 2>&1 etc are found and replaced or just removed for better understanding. 
    command string is also de-indented and generally cleaned (blank lines removed etc)
    process
    """
    def __init__(self, tooldef: GalaxyToolDefinition):
        self.tooldef = tooldef

    def load(self) -> str:
        return self.tooldef.command
       




        
    
    
    
    