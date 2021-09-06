
#pyright: strict

from typing import Optional

#from classes.datastructures import Param

 
class Tool:
    def __init__(self):
        self.name: str = ""
        self.command: Optional[str] = None  # placeholder for now
        self.version: str = ""
        self.creator: str = ""
        self.containers: dict[str, str] = {} # from requirements tag
        self.tool_module: str = 'bioinformatics' 
        self.params = []  
        self.outputs = []
        self.tests: list[dict[str, str]] = []
        self.help: str = ""
        self.citations: str = ""
