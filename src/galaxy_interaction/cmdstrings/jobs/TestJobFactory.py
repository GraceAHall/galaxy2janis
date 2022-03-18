


from typing import Any
from galaxy_interaction.cmdstrings.jobs.JobFactorytest import JobFactory
from galaxy.tool_util.verify.interactor import ToolTestDescription


class TestJobFactory(JobFactory):
    test: ToolTestDescription

    def create(self, app: MockApp, history: History, test: ToolTestDescription, xmltool: XMLToolDefinition) -> Optional[Job]:
        self.refresh_attributes(app, history, test, xmltool)
        self.set_job_inputs()
        self.set_job_outputs()
        return self.job

    def refresh_attributes(self, app: MockApp, history: History, test: ToolTestDescription, xmltool: XMLToolDefinition) -> None:
        self.app = app
        self.test = test
        self.xmltool = xmltool
        self.input_dict = self.xmltool.dict_inputs()
        self.job = self.init_job(history)

    def set_job_inputs(self) -> None:  
        self.set_input_dict()
        self.override_input_values()
        self.jsonify_job_inputs()
        self.set_job_parameters()

    def inject_supplied_values(self) -> None:
        test_inputs: dict[str, Any] = self.test.inputs
        for pname, pvalue in test_inputs.items():
            pname = self.format_param_name(pname)     # param name
            pvalue = self.format_param_value(pvalue)  # param value
            self.handle_input_param(pname, pvalue)

    def set_job_outputs(self) -> None:
        # note i think out is an object not a str
        for out in self.test.outputs:
            output_var = str(out['name'].replace('|', '.'))
            job_output = datasets.generate_output_dataset(self.app, output_var, out['attributes']['ftype'])
            self.job.output_datasets.append(job_output)