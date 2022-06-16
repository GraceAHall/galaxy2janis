


#from gx_src.tools import Tool as GalaxyTool
from abc import ABC, abstractmethod
import os
import json
from typing import Any, Optional, Tuple

from galaxy.tool_util.verify.interactor import ToolTestDescription
from runtime.settings.ExeSettings import ToolExeSettings
from galaxy.model import Job, JobParameter
import galaxy_interaction.cmdstrings.test_commands.datasets as datasets
from galaxy_interaction.mock import MockApp
from xmltool.param.Param import Param
from xmltool.param.InputParam import DataParam, DataCollectionParam

from xmltool.XMLToolDefinition import XMLToolDefinition

from galaxy.model import (
    History,
    Job,
    JobParameter
)


class JobFactory(ABC):
    app: MockApp
    history: History
    xmltool: XMLToolDefinition
    job: Job
    input_dict: dict[str, Any]

    def __init__(self, esettings: ToolExeSettings):
        self.esettings = esettings
    
    @abstractmethod
    def create(self, app: MockApp, history: History, xmltool: XMLToolDefinition) -> Optional[Job]:
        ...

    @abstractmethod
    def refresh_attributes(self, app: MockApp, test: ToolTestDescription, xmltool: XMLToolDefinition) -> None:
        ...
    
    @abstractmethod
    def set_job_inputs(self) -> None:
        ...

    @abstractmethod
    def inject_supplied_values(self) -> None:
        ...
    
    @abstractmethod
    def set_job_outputs(self) -> None:
        ...

    # Common methods with concrete definitions
    def init_job(self, history: History) -> Job:
        job = Job()
        job.history = history
        job.history.id = 1337
        return job

    def format_param_name(self, pname: str) -> str:
        return pname.replace('|', '.') 
    
    def format_param_value(self, pvalue: Any) -> Any:
        # TODO REMOVE THIS ITS A BAD HACK TO AVOID ARRAYS
        if isinstance(pvalue, list):
            return pvalue[0]
        return pvalue

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
    
    def get_test_data_path(self, filename: str) -> str:
        return f'{self.esettings.get_tool_test_dir()}/{filename}'

    def set_job_parameters(self) -> None:
        self.job.parameters = [JobParameter(name=k, value=v) for k, v in self.input_dict.items()]


    


    def handle_input_param(self, pname: str, pvalue: Any) -> None:
        if self.is_data_input(pvalue):
            self.handle_data_param(pname, pvalue)
        else:
            self.handle_non_data_param(pname, pvalue)

    def is_data_input(self, pvalue: str) -> bool:
        required_files: list[Tuple[str, dict[str, Any]]] = self.test.required_files
        for filename, _ in required_files:
            if filename == pvalue:
                return True
        return False

    def handle_non_data_param(self, pname: str, pvalue: Any) -> None:
        self.update_job_input_tree(pname, pvalue)

    def handle_data_param(self, pname: str, filename: Any) -> None:
        data_path = self.get_test_data_path(filename)
        if os.path.exists(filepath):
            job_input = datasets.generate_input_dataset(self.app, pname, data_path)
            self.job.input_datasets.append(job_input)
            self.update_job_input_tree(pname, str(job_input.dataset.dataset_id))
        else:
            raise RuntimeError(f'test data {filename} could not be found at {data_path}')





