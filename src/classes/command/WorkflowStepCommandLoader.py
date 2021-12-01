

from typing import Any
from galaxy.tools import Tool as GalaxyTool
from classes.logging.Logger import Logger


class WorkflowStepCommandLoader:
    """
    loads a valid command string from the combination of a galaxy tool and 
    workflow step parameter dict
    
    Uses galaxy code to template the galaxy tool and the parameter dict into
    a valid command string

    """
    def __init__(self, gxtool: GalaxyTool, logger: Logger):
        self.gxtool = gxtool
        self.logger = logger


    def load(self, workflow_step: dict[str, Any]) -> list[str]:
        pass