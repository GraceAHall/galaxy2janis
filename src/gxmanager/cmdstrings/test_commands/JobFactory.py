


#from gx_src.tools import Tool as GalaxyTool
import json
from typing import Any, Optional

from galaxy.tool_util.verify.interactor import ToolTestDescription

from galaxy.model import Job, JobParameter
from gxmanager.cmdstrings.test_commands.datasets import generate_dataset
from gxmanager.mock import MockApp
from tool.param.Param import Param
from tool.param.InputParam import DataParam, DataCollectionParam

from tool.tool_definition import GalaxyToolDefinition

from galaxy.model import (
    History,
    Job,
    JobParameter
)


class JobFactory:
    
    def create(self, app: MockApp, history: History, test: ToolTestDescription, tool: GalaxyToolDefinition) -> Optional[Job]:
        self.refresh_attributes(app, test, tool)
        self.init_job(history)
        self.set_job_inputs()
        self.handle_test_values()
        self.jsonify_job_inputs()
        self.set_job_parameters()
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
        self.job_inputs: dict[str, Any] = self.tool.get_inputs(format='dict')

    def handle_test_values(self) -> None:
        tvalues: dict[str, Any] = self.test.inputs
        for pname, pvalue in tvalues.items():
            if isinstance(pvalue, list):
                pvalue = pvalue[0]
            pname = pname.replace('|', '.')
            input_param = self.tool.get_input(pname, strategy='lca')
            if input_param:
                self.handle_input_param(input_param, pvalue)
            else:
                raise RuntimeError(f'could not find param {pname}')

    def handle_input_param(self, param: Param, override_value: Any) -> None:
        match param:
            case DataParam():
                job_input = generate_dataset(self.app, param.name, 'input')
                self.job.input_datasets.append(job_input)
                self.update_job_input_tree(param.name, str(job_input.dataset.dataset_id)) 
            case DataCollectionParam():
                raise NotImplementedError
            case _:
                self.update_job_input_tree(param.name, override_value)

    def update_job_input_tree(self, paramname: str, value: Any) -> None:
        param_path = paramname.split('.')
        tree = self.job_inputs
        for i, text in enumerate(param_path):
            if i == len(param_path) - 1:
                tree[text] = value
            else:
                tree = tree[text]

    def jsonify_job_inputs(self) -> None:
        for key, val in self.job_inputs.items():
            if type(val) == dict:
                self.job_inputs[key] = json.dumps(val)  

    def set_job_parameters(self) -> None:
        self.job.parameters = [JobParameter(name=k, value=v) for k, v in self.job_inputs.items()]

    def set_job_outputs(self) -> None:
        # note i think out is an object not a str
        for out in self.test.outputs:
            output_var = str(out['name'].replace('|', '.'))
            job_output = generate_dataset(self.app, output_var, 'output')
            self.job.output_datasets.append(job_output)





    # def set_job_dict(self) -> None:
    #     self.test_values: dict[str, Any] = self.test.inputs
    # def get_test_values_reducearray(test: ToolTestDescription) -> dict[str, Any]:
    #     """maybe the following is needed"""
    #     test_values: dict[str, Any] = {}
    #     for label, values in test.inputs.items():
    #         if len(values) == 1:
    #             test_values[str(label)] = values[0]
    #         else:
    #             test_values[str(label)] = values
    #     return test_values


# old
    def update_test_inputs_old(label: str, values: list[str], param_dict: dict, job: Job) -> None:
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