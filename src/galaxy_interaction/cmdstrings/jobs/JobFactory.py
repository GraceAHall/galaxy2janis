
#from gx_src.tools import Tool as GalaxyTool
import os
import json
from typing import Any, Optional, Tuple

from galaxy.tool_util.verify.interactor import ToolTestDescription
from startup.ExeSettings import ToolExeSettings
from galaxy.model import Job, JobParameter
import galaxy_interaction.cmdstrings.dataset_utils as dataset_utils
from galaxy_interaction.mock import MockApp
from xmltool.param.Param import Param
from xmltool.param.InputParam import DataParam, DataCollectionParam

from xmltool.tool_definition import XMLToolDefinition

from galaxy.model import (
    History,
    Job,
    JobParameter
)


"""
files = {
    'paramname': {
        'filepath': 'str',
        'ftype': 'str',
    },
}
input_values = {
    'paramname': 'value',
    'paramname': 'value',
}
output_values = {
    'outname': 'ftype'?
}

"""


class JobFactory:
    app: MockApp
    history: History
    xmltool: XMLToolDefinition
    files: dict[str, Any]
    input_values: dict[str, Any]
    output_values: dict[str, Any]
    job_dict: dict[str, Any]

    def __init__(self, esettings: ToolExeSettings):
        self.esettings = esettings
    
    def create(
        self, 
        app: MockApp,
        history: History,
        xmltool: XMLToolDefinition,
        files: dict[str, Any],
        input_values: dict[str, Any],
        output_values: dict[str, Any]
    ) -> Optional[Job]:
        self.refresh_objects(app, history, xmltool)
        self.refresh_data(files, input_values, output_values)
        self.set_job_parameters()
        self.set_job_outputs()
        return self.job

    def refresh_objects(self, app: MockApp, history: History, xmltool: XMLToolDefinition) -> None:
        self.app = app
        self.xmltool = xmltool
        self.job = self.init_job(history)
    
    def init_job(self, history: History) -> Job:
        job = Job()
        job.history = history
        job.history.id = 1337
        return job

    def refresh_data(self, files: dict[str, Any], input_values: dict[str, Any], output_values: dict[str, Any]) -> None:
        self.files = files
        self.input_values = input_values
        self.output_values = output_values
        self.job_dict: dict[str, Any] = self.xmltool.dict_inputs()

    def set_job_parameters(self) -> None: 
        self.inject_supplied_input_values()
        self.jsonify_job_dict()
        self.job.parameters = [JobParameter(name=k, value=v) for k, v in self.job_dict.items()]

    def inject_supplied_input_values(self) -> None:
        for pname, pvalue in self.input_values.items():
            pname = self.format_param_name(pname)     # param name
            pvalue = self.format_param_value(pvalue)  # param value
            self.handle_input_param(pname, pvalue)

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
        for filename, _ in self.files:
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
        return f'{self.esettings.get_tool_test_dir()}/{filename}'

    def file_exists(self, filepath: str) -> bool:
        if os.path.exists(filepath):
            return True
        return False

    def update_job_input_tree(self, paramname: str, value: Any) -> None:
        param_path = paramname.split('.')
        tree = self.job_dict
        for i, text in enumerate(param_path):
            if i == len(param_path) - 1:
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

    def set_job_outputs(self) -> None:
        for out in self.output_values:
            output_var = str(out['name'].replace('|', '.'))
            job_output = dataset_utils.generate_output_dataset(self.app, output_var, out['attributes']['ftype'])
            self.job.output_datasets.append(job_output)