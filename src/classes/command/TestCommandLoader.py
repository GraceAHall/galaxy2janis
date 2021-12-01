

from galaxy.tools import Tool as GalaxyTool
from classes.logging.Logger import Logger

from galaxy.tool_util.verify.interactor import ToolTestDescription


class TestCommandLoader:
    """
    loads a valid command string from the combination of a galaxy tool and an xml test

    Uses planemo code to load test cases into parameter dict
    Uses galaxy code to template the galaxy tool and the parameter dict 
    into a valid command string

    """
    def __init__(self, gxtool: GalaxyTool, logger: Logger):
        self.gxtool = gxtool
        self.logger = logger


    def load(self, test: ToolTestDescription) -> list[str]:
        pass