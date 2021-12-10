

#from galaxy.tools import Tool as GalaxyTool
import tempfile
from typing import Optional

from galaxy.tools import Tool as GalaxyTool
from galaxy.tool_util.verify.interactor import ToolTestDescription

from galaxy.model import Job, JobParameter
from classes.templating.MockClasses import MockApp
from classes.tool.Tool import Tool
from classes.logging.Logger import Logger

from utils.galaxy_utils import generate_dataset, setup_evaluator


class TestCommandLoader:
    """
    loads a valid command string from the combination of a galaxy tool and an xml test

    Uses planemo code to load test cases into parameter dict
    Uses galaxy code to template the galaxy tool and the parameter dict 
    into a valid command string

    """
    def __init__(self, app: MockApp, gxtool: GalaxyTool, tool: Tool, logger: Logger):
        self.app = app
        self.gxtool = gxtool
        self.tool = tool
        self.test_directory = tempfile.mkdtemp()  
        self.logger = logger
        

    def load(self, test: ToolTestDescription) -> Optional[list[str]]:
        """comment"""
        job = self.setup_job(test)
        # setup_job() will return None if there are errors creating a job
        # at the moment only repeat params should cause setup_job() to return None
        if job is None:
            return None

        evaluator = setup_evaluator(self.app, self.gxtool, job, self.test_directory)
        command_line, _, __ = evaluator.build()
        return [command_line]


    def setup_job(self, test: ToolTestDescription) -> Optional[Job]:
        job = Job()
        
        defined_inputs = {}
        for name, values in test.inputs.items():
            self.update_test_inputs(name, values, defined_inputs, job)

        job_dict = self.tool.param_register.to_job_dict(value_overrides=defined_inputs)
        
        # incase anything went wrong in the job_dict creation phase
        if job_dict is None:
            return None
        
        job.parameters = [JobParameter(name=k, value=v) for k, v in job_dict.items()]
        
        for out in self.gxtool.outputs:
            self.update_test_outputs(out, job)
        
        return job


    def update_test_inputs(self, label: str, values: list[str], param_dict: dict, job: Job) -> None:
        # get the param variable name and param
        query_var = label.replace('|', '.')
        varname, param = self.tool.param_register.get(query_var, allow_lca=True)
        # allowing lca means repeat params are properly found. shouldn't affect anything else? the returned param_var in case of repeats has a different name to query_var.
        
        # creating (fake) datasets for the data inputs and outputs
        # each repeat in a repeat param which is type="data" will 
        # be fed individually here, with a unique name, so all good. 
        if param.type == 'data':
            job_input = generate_dataset(self.app, varname, 'input')
            job.input_datasets.append(job_input)
            param_dict[query_var] = str(job_input.dataset.dataset_id)
        
        # no idea what to do here
        elif param.type == 'data_collection':
            pass

        # not a data input param
        else:   
            if len(values) == 1:
                param_dict[varname] = values[0]
            else:
                param_dict[varname] = values


    def update_test_outputs(self, label: str, job: Job) -> None:
        output_var = label.replace('|', '.')
        job_output = generate_dataset(self.app, output_var, 'output')
        job.output_datasets.append(job_output)




        
