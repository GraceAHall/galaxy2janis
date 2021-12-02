

#from galaxy.tools import Tool as GalaxyTool
import tempfile
from typing import Union

from classes.templating.MockClasses import MockApp, ComputeEnvironment
from classes.tool.Tool import Tool
from galaxy.tools import Tool as GalaxyTool
from classes.logging.Logger import Logger
from classes.error_handling.Exceptions import ParamExistsException

from galaxy.tool_util.verify.interactor import ToolTestDescription
from galaxy.model import (
    Job,
    JobParameter,
    Dataset,
    HistoryDatasetAssociation,
    JobToInputDatasetAssociation,
    JobToOutputDatasetAssociation,
)
from galaxy.tools.evaluation import ToolEvaluator

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
        self.dataset_counter: int = 1


    def load(self, test: ToolTestDescription) -> list[str]:
        """comment"""
        job = self.setup_job(test)
        evaluator = self.setup_evaluator(job)
        command_line, _, __ = evaluator.build()
        print('\n', command_line)
        return command_line


    def setup_job(self, test: ToolTestDescription) -> Job:
        job = Job()
        
        param_dict = {}
        for name, values in test.inputs.items():
            self.update_defined_inputs(name, values, param_dict, job)

        job_dict = self.tool.param_register.to_job_dict(value_overrides=param_dict)
        job.parameters = [JobParameter(name=k, value=v) for k, v in job_dict.items()]
        
        for out in test.outputs:
            self.update_defined_outputs(out['name'], job)
        
        return job


    def update_defined_inputs(self, label: str, values: list[str], param_dict: dict, job: Job) -> None:
        # get the param variable name and param
        query_var = label.replace('|', '.')
        param_var, param = self.tool.param_register.get(query_var)
        
        # creating (fake) datasets for the data inputs and outputs
        if param.type == 'data':
            job_input = self.gen_dataset(values[0], 'input')
            param_dict[param_var] = str(job_input.dataset.dataset_id)
            job.input_datasets.append(job_input)
        elif param.type == 'data_collection':
            pass
        # TODO OUTPUTS? 

        # not a data input / output param
        else:   
            if len(values) == 1:
                param_dict[param_var] = values[0]
            else:
                param_dict[param_var] = values


    def update_defined_outputs(self, label: str, job: Job) -> None:
        output_var = label.replace('|', '.')
        job_output = self.gen_dataset(output_var, 'output')
        job.output_datasets.append(job_output)
        print()


    def gen_dataset(self, fname: str, iotype: str) -> Union[JobToInputDatasetAssociation, JobToOutputDatasetAssociation]:
        """
        creates a dataset association. 
        this process creates a dataset and updates the sql database model.
        """
        i, path = self.dataset_counter, fname
        self.dataset_counter += 1

        if iotype == 'input':
            return JobToInputDatasetAssociation(name=fname, dataset=self.gen_hda(i, fname, path))
        elif iotype == 'output':
            return JobToOutputDatasetAssociation(name=fname, dataset=self.gen_hda(i, fname, path))


    def gen_hda(self, id, name, path) -> HistoryDatasetAssociation:
        hda = HistoryDatasetAssociation(name=name, metadata=dict())
        hda.dataset = Dataset(id=id, external_filename=path)
        hda.dataset.metadata = dict()
        hda.children = []
        self.app.model.context.add(hda)
        self.app.model.context.flush()
        return hda
    

    def setup_evaluator(self, job: Job) -> ToolEvaluator:
        evaluator = ToolEvaluator(self.app, self.gxtool, job, self.test_directory)
        kwds = {}
        kwds["working_directory"] = self.test_directory
        kwds["new_file_path"] = self.app.config.new_file_path
        evaluator.set_compute_environment(ComputeEnvironment(**kwds))
        return evaluator

        
