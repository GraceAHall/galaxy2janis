

from copy import deepcopy
import json
import tempfile
from typing import Union, Optional, Any

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


class WorkflowStepCommandLoader:
    """
    loads a valid command string from the combination of a galaxy tool and 
    workflow step parameter dict
    
    Uses galaxy code to template the galaxy tool and the parameter dict into
    a valid command string

    """
    def __init__(self, app: MockApp, gxtool: GalaxyTool, tool: Tool, logger: Logger):
        self.app = app
        self.gxtool = gxtool
        self.tool = tool
        self.test_directory = tempfile.mkdtemp()  
        self.logger = logger


    def load(self, workflow: dict[str, Any], workflow_step: int) -> Optional[list[str]]:
        """comment"""

        job = self.setup_job(workflow, workflow_step)
        # setup_job() will return None if there are errors creating a job
        # at the moment only repeat param should cause setup_job() to return None
        if job is None:
            return None

        evaluator = self.setup_evaluator(job)
        command_line, _, __ = evaluator.build()
        return [command_line]


    def setup_job(self, workflow: dict[str, Any], workflow_step: int) -> Optional[Job]:
        job = Job()
        job_state = self.load_job_state(workflow, workflow_step)
        job_state = self.replace_special_vars(job_state, [], job)
        job_state = self.jsonify_job_state(job_state)
        
        # incase anything went wrong in the job_state creation phase
        if job_state is None:
            return None
        
        job.parameters = [JobParameter(name=k, value=v) for k, v in job_state.items()]
        
        for out in self.gxtool.outputs:
            self.update_job_outputs(out, job)
        
        return job


    def load_job_state(self, workflow: dict[str, Any], workflow_step: int) -> dict:
        with open(workflow, 'r') as fp:
            data = json.load(fp)
        return json.loads(data['steps'][str(workflow_step)]['tool_state'])


    def replace_special_vars(self, node: dict, treepath: list[str], job: Job) -> dict:
        node = dict([(k, v) for k, v in node.items() if k != '__current_case__'])
        
        for pkey, pval in node.items():
            if type(pval) == dict:
                newpath = deepcopy(treepath + [pkey])
                newval = self.attempt_value_replacement(pval, newpath, job)
                if newval is not None:
                    node[pkey] = newval
                else:
                    node[pkey] = self.replace_special_vars(pval, newpath, job)

        return node


    def attempt_value_replacement(self, node: dict, treepath: list[str], job: Job) -> Optional[str]:
        nodekeys = list(node.keys())
        if len(nodekeys) == 1:
            key = nodekeys[0]
            val = node[nodekeys[0]]
            if key == '__class__' and val in ['ConnectedValue', 'RuntimeValue']:
                query_key = '.'.join(treepath)
                varname, param = self.tool.param_register.get(query_key)
                
                if param.type == 'data':
                    job_input = self.generate_dataset(query_key, 'input')
                    job.input_datasets.append(job_input)
                    return str(job_input.dataset.dataset_id)

                else:
                    default = self.tool.param_register.get_param_default_value(param)
                    return str(default)

        return None


    def jsonify_job_state(self, job_state: dict) -> dict:
        for key, val in job_state.items():
            if type(val) == dict:
                job_state[key] = json.dumps(val)  
        return job_state


    def update_job_outputs(self, label: str, job: Job) -> None:
        output_var = label.replace('|', '.')
        job_output = self.generate_dataset(output_var, 'output')
        job.output_datasets.append(job_output)


    def generate_dataset(self, fname: str, iotype: str) -> Union[JobToInputDatasetAssociation, JobToOutputDatasetAssociation]:
        """
        creates a dataset association. 
        this process creates a dataset and updates the sql database model.
        """
        i, path = self.app.dataset_counter, fname
        self.app.dataset_counter += 1

        if iotype == 'input':
            return JobToInputDatasetAssociation(name=fname, dataset=self.generate_hda(i, fname, path))
        elif iotype == 'output':
            return JobToOutputDatasetAssociation(name=fname, dataset=self.generate_hda(i, fname, path))


    def generate_hda(self, id, name, path) -> HistoryDatasetAssociation:
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