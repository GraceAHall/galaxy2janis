
#from gx_src.tools import Tool as GalaxyTool
import os
import json
from typing import Any, Optional

from runtime.contexts import nostdout
from startup.ExeSettings import ToolExeSettings
from galaxy.model import Job, JobParameter
import galaxy_interaction.cmdstrings.dataset_utils as dataset_utils
from galaxy_interaction.mock import MockApp
from galaxy.tool_util.verify.interactor import ToolTestDescription
from startup.ExeSettings import ToolExeSettings

from galaxy.model import (
    History,
    Job,
    JobParameter
)

from xmltool.tool_definition import XMLToolDefinition


class JobFactory:
    job: Job 
    
    def __init__(self, esettings: ToolExeSettings, app: MockApp, history: History, test: ToolTestDescription, xmltool: XMLToolDefinition):
        self.esettings = esettings
        self.app = app
        self.history = history
        self.test = test
        self.xmltool = xmltool
        self.job_dict: dict[str, Any] = {}
    
    def create(
        self
        #files: dict[str, Any],
        #input_values: dict[str, Any],
        #output_values: dict[str, Any]
    ) -> Optional[Job]:
        self.job = self.init_job()
        self.set_inputs()
        self.set_outputs()
        return self.job

    def init_job(self) -> Job:
        job = Job()
        job.history = self.history
        job.history.id = 1337
        return job
        
    def set_inputs(self) -> None:
        self.supply_supplied_job_dict_values()
        self.supply_remaining_job_dict_values()
        self.jsonify_job_dict()
        self.set_job_parameters()

    def supply_supplied_job_dict_values(self) -> None:
        for pname, pvalue in self.test.inputs.items():
            pname = self.format_param_name(pname)     # param name
            pvalue = self.format_param_value(pvalue)  # param value
            self.handle_input_param(pname, pvalue)

    def supply_remaining_job_dict_values(self) -> None:
        for param in self.xmltool.list_inputs():
            pname = self.format_param_name(param.name)     # param name
            pvalue = self.format_param_value(param.get_default())  # param value
            self.handle_input_param(pname, pvalue)
        
    def set_job_parameters(self) -> None: 
        self.job.parameters = [JobParameter(name=k, value=v) for k, v in self.job_dict.items()]

    def format_param_name(self, pname: str) -> str:
        return pname.replace('|', '.') 

    def format_param_value(self, pvalue: Any) -> Any:
        # TODO REMOVE THIS ITS A BAD HACK TO AVOID ARRAYS
        if isinstance(pvalue, list):
            return pvalue[0]
        return pvalue

    def handle_input_param(self, pname: str, pvalue: Any) -> None:
        if self.is_data_input(pvalue):
            self.handle_data_param(pname, pvalue)
        else:
            self.handle_non_data_param(pname, pvalue)

    def is_data_input(self, pvalue: str) -> bool:
        for filename, _ in self.test.required_files:
            if filename == pvalue:
                return True
        return False

    def handle_non_data_param(self, pname: str, pvalue: Any) -> None:
        self.update_job_input_tree(pname, pvalue)

    def handle_data_param(self, pname: str, filename: Any) -> None:
        data_path = self.get_test_data_path(filename)
        if self.file_exists(data_path):
            job_input = dataset_utils.generate_input_dataset(self.app, pname, data_path)
            self.job.input_datasets.append(job_input)
            self.update_job_input_tree(pname, str(job_input.dataset.dataset_id))
        else:
            raise RuntimeError(f'test data {filename} could not be found at {data_path}')

    def get_test_data_path(self, filename: str) -> str:
        return f'{self.esettings.xmldir}/test-data/{filename}'

    def file_exists(self, filepath: str) -> bool:
        if os.path.exists(filepath):
            return True
        return False

    def update_job_input_tree(self, paramname: str, value: Any) -> None:
        param_path = paramname.split('.')
        tree = self.job_dict
        for i, text in enumerate(param_path):
            if i == len(param_path) - 1:
                if text not in tree: # don't override existing value
                    tree[text] = value
            elif text not in tree:
                tree[text] = {}
                tree = tree[text]
            else:
                tree = tree[text]

    def jsonify_job_dict(self) -> None:
        for key, val in self.job_dict.items():
            if type(val) == dict:
                self.job_dict[key] = json.dumps(val)  

    def set_outputs(self) -> None:
        for out in self.test.outputs:
            param_name = str(self.format_param_name(out['name']))
            gx_datatype = out['attributes']['ftype']
            job_output = dataset_utils.generate_output_dataset(self.app, param_name, gx_datatype)
            self.job.output_datasets.append(job_output)