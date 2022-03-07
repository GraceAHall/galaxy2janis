


#from gx_src.tools import Tool as GalaxyTool
import os
import json
from typing import Any, Optional, Tuple

from galaxy.tool_util.verify.interactor import ToolTestDescription
from startup.ExeSettings import ToolExeSettings
from galaxy.model import Job, JobParameter
import galaxy_interaction.cmdstrings.test_commands.datasets as datasets
from galaxy_interaction.mock import MockApp
from tool.param.Param import Param
from tool.param.InputParam import DataParam, DataCollectionParam

from tool.tool_definition import GalaxyToolDefinition

from galaxy.model import (
    History,
    Job,
    JobParameter
)


class JobFactory:
    app: MockApp
    history: History
    test: ToolTestDescription
    tool: GalaxyToolDefinition

    def __init__(self, esettings: ToolExeSettings):
        self.esettings = esettings
    
    def create(self, app: MockApp, history: History, test: ToolTestDescription, tool: GalaxyToolDefinition) -> Optional[Job]:
        self.refresh_attributes(app, test, tool)
        self.init_job(history)
        self.set_job_inputs()
        self.set_job_outputs()
        return self.job

    def refresh_attributes(self, app: MockApp, test: ToolTestDescription, tool: GalaxyToolDefinition) -> None:
        self.app = app
        self.test = test
        self.tool = tool
        self.job = Job()

    def init_job(self, history: History) -> None:
        # unsure if following two lines are needed
        self.job.history = history
        self.job.history.id = 1337

    def set_job_inputs(self) -> None:  
        self.set_input_dict()
        self.handle_test_values()
        self.jsonify_job_inputs()
        self.set_job_parameters()

    def set_input_dict(self) -> None:
        self.input_dict: dict[str, Any] = self.tool.dict_inputs()

    def handle_test_values(self) -> None:
        test_inputs: dict[str, Any] = self.test.inputs
        for pname, pvalue in test_inputs.items():
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
        if self.is_required_file(pvalue):
            self.handle_data_param(pname, pvalue)
        else:
            self.handle_non_data_param(pname, pvalue)

    def is_required_file(self, pvalue: str) -> bool:
        required_files: list[Tuple[str, dict[str, Any]]] = self.test.required_files
        for filename, _ in required_files:
            if filename == pvalue:
                return True
        return False

    def handle_non_data_param(self, pname: str, pvalue: Any) -> None:
        self.update_job_input_tree(pname, pvalue)

    def handle_data_param(self, pname: str, filename: Any) -> None:
        data_path = self.get_test_data_path(filename)
        if self.file_exists(data_path):
            job_input = datasets.generate_input_dataset(self.app, pname, data_path)
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
        tree = self.input_dict
        for i, text in enumerate(param_path):
            if i == len(param_path) - 1:
                tree[text] = value
            elif text not in tree:
                tree[text] = {}
                tree = tree[text]
            else:
                tree = tree[text]

    def jsonify_job_inputs(self) -> None:
        for key, val in self.input_dict.items():
            if type(val) == dict:
                self.input_dict[key] = json.dumps(val)  

    def set_job_parameters(self) -> None:
        self.job.parameters = [JobParameter(name=k, value=v) for k, v in self.input_dict.items()]

    def set_job_outputs(self) -> None:
        # note i think out is an object not a str
        for out in self.test.outputs:
            output_var = str(out['name'].replace('|', '.'))
            job_output = datasets.generate_output_dataset(self.app, output_var, out['attributes']['ftype'])
            self.job.output_datasets.append(job_output)


