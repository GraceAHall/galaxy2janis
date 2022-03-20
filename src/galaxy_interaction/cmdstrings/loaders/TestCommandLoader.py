

import tempfile
from typing import Optional
from startup.ExeSettings import ToolExeSettings
from runtime.Logger import Logger

from xmltool.tool_definition import XMLToolDefinition
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
        self.jobfactory = JobFactory(self.esettings)
        
    def load(self, test: ToolTestDescription) -> Optional[str]:
        try:
            job = self.jobfactory.create(
                self.app,
                self.history,
                self.toolrep,
                test.required_files, # type: ignore god I hate galaxy no type hinting
                test.inputs, # type: ignore
                test.outputs # type: ignore
            ) 
            if job:
                evaluator = self.setup_evaluator(self.app, self.gxtool, job)
                command_line, _, __ = evaluator.build()
                return command_line
        except Exception as e:
            print(e)
            logger = Logger(self.esettings.get_logfile_path())
            logger.log(1, 'test failed to template')
            return None

    def setup_evaluator(self, app: MockApp, gxtool: GxTool, job: Job) -> ToolEvaluator:
        evaluator = ToolEvaluator(app, gxtool, job, self.test_directory)
        kwds = {}
        kwds["working_directory"] = self.test_directory
        kwds["new_file_path"] = app.config.new_file_path
        evaluator.set_compute_environment(ComputeEnvironment(**kwds))
        return evaluator


