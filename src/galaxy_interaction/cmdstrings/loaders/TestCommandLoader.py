

import logging 
import tempfile
from typing import Optional
from runtime.ExeSettings import ToolExeSettings

from xmltool.XMLToolDefinition import XMLToolDefinition
from galaxy.tools import Tool as GxTool
from galaxy.tool_util.verify.interactor import ToolTestDescription

from galaxy.model import Job, History
from galaxy_interaction.mock import MockApp, ComputeEnvironment
from galaxy_interaction.cmdstrings.jobs.JobFactory import JobFactory

from galaxy.tools.evaluation import ToolEvaluator


class TestCommandLoader:
    """
    loads a valid command string from the combination of a galaxy tool and an xml test

    Uses internal code to load test cases into parameter dict and set up job
    Uses galaxy code to template the galaxy tool and the parameter dict 
    into a valid command string
    """
    def __init__(self, app: MockApp, history: History, gxtool: GxTool, toolrep: XMLToolDefinition, esettings: ToolExeSettings):
        self.app = app
        self.history = history
        self.gxtool = gxtool
        self.toolrep = toolrep
        self.esettings = esettings
        self.test_directory = tempfile.mkdtemp()
        self.dataset_counter: int = 1
        
    def load(self, test: ToolTestDescription) -> Optional[str]:
        try:
            factory = JobFactory(
                self.esettings,
                self.app,
                self.history,
                test,
                self.toolrep
            ) 
            job = factory.create()
            if job:
                evaluator = self.setup_evaluator(self.app, self.gxtool, job)
                command_line, _, __ = evaluator.build()
                return command_line
        except Exception:
            logger = logging.getLogger('gxtool2janis')
            logger.debug('test failed to template')
            return None

    def setup_evaluator(self, app: MockApp, gxtool: GxTool, job: Job) -> ToolEvaluator:
        evaluator = ToolEvaluator(app, gxtool, job, self.test_directory)
        kwds = {}
        kwds["working_directory"] = self.test_directory
        kwds["new_file_path"] = app.config.new_file_path
        evaluator.set_compute_environment(ComputeEnvironment(**kwds))
        return evaluator



