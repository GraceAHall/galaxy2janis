


# pyright: basic

import json
import threading
from typing import Union
from pydantic.types import Json 
import tempfile
import os

from galaxy.tools.evaluation import ToolEvaluator
from galaxy.tools.parameters.grouping import Section
from galaxy.tool_util.toolbox.views.definitions import Tool
from galaxy.tool_util.parser import get_tool_source
from galaxy.tools import create_tool_from_source
from galaxy.model import (
    History,
    Job,
    JobParameter,
    Dataset,
    HistoryDatasetAssociation,
    JobToInputDatasetAssociation,
    JobToOutputDatasetAssociation,
)

from classes.templating.MockClasses import MockTool, MockApp, MockObjectStore, ComputeEnvironment


class Templator:
    def __init__(self, tool_file: str, tool_dir: str) -> None:
        self.tool_file = tool_file
        self.tool_dir = tool_dir
        self.test_directory = tempfile.mkdtemp()  
        self.history = History()  # a history object (which history id should the outputs go? etc)
        self.use_mock_tool = False
        self.dataset_counter = 1


    def init_objects(self) -> None:
        self.app = self.init_app()
        self.tool = self.init_tool()
        self.job = self.init_job() 
        #self.compute_environment = self.init_compute_env()
        self.evaluator = ToolEvaluator(self.app, self.tool, self.job, self.test_directory)


    def init_app(self) -> MockApp:
        app = MockApp()
        app.config.new_file_path = os.path.join(self.test_directory, "new_files")
        app.config.admin_users = "mary@example.com"
        app.job_search = None
        app.model.context.add(self.history)
        app.model.context.flush()
        app.config.len_file_path = "moocow"
        app.object_store = MockObjectStore()
        return app


    def init_tool(self) -> Tool:
        if self.use_mock_tool:
            return self.init_tool_from_mocktool()
        else:
            return self.init_tool_from_xml(self.tool_dir, self.tool_file)


    def init_tool_from_mocktool(self) -> Tool:
        return MockTool(self.app)


    def init_tool_from_xml(self, tool_dir, tool_file):
        tool_path = os.path.join(tool_dir, tool_file)
        tool_source = get_tool_source(tool_path)
        tool = create_tool_from_source(self.app, tool_source, config_file=tool_path)
        tool.assert_finalized()
        return tool


    def init_job(self) -> Job:
        job = Job()
        job.history = self.history 
        job.history.id = 42
        return job

    
    def setup_job(self, workflow_step: Json = None) -> None:
        self.job.parameters = self.setup_job_params(workflow_step)
        self.job.input_datasets = self.setup_input_associations(workflow_step)
        self.job.output_datasets = self.setup_output_associations(workflow_step)
        print()


    def setup_job_params(self, workflow_step: Json=None) -> list[JobParameter]: 
        # job_state contains the tool param values for a workstep step 
        # the default behaviour is to load tool param values from tool tests in the xml
        # but if job_state is supplied, it gets param values from there instead
        if workflow_step is None:
            param_dict = self.get_param_dict_from_test(test_item=0)
        else:
            param_dict = self.get_param_dict_from_workflow_step(workflow_step)
        
        # turn them all into JobParameters
        return [JobParameter(name=k, value=v) for k, v in param_dict.items()]


    def get_param_dict_from_test(self, test_item: int=0) -> dict:
        # abricate
        return {   
            'file_input': '1',
            'adv': json.dumps({
                'db': 'resfinder',
                'no_header': False,
                'min_dna_id': 80,
                'min_cov': None,
        })}

        # busco
        return {   
            'input': '1',
            'busco_mode': json.dumps({
                'mode': 'geno',
                'use_augustus': {
                    'use_augustus_selector': 'yes'
                }
            }),
            'lineage_dataset'
            'adv': json.dumps({
                'outputs': 'short_summary,missing'
            })
        }
        

        # TODO remove hard coded test item
        params = self.inputs_to_param_dict(self.tool.inputs)
        test = self.tool.tests[4]
        
        example = {   
            'file_input': 'hello.txt',
            'adv': json.dumps({
                'db': 'resfinder',
                'no_header': False,
                'min_dna_id': 80,
                'min_cov': None,
        })}

        print()


    def inputs_to_param_dict(self, inputs: dict) -> dict:
        out = {}
        for name, obj in inputs.items():
            if isinstance(obj, Section):
                out[obj.name] = None
            else:
                print()
        
        return out


    def get_param_dict_from_workflow_step(self, workflow_step: Json) -> dict:
        pass


    def setup_input_associations(self, workflow_step: Json=None) -> list[JobToInputDatasetAssociation]:
        if workflow_step is None:
            inputs = self.get_inputs_from_test(test_item=0)
        else:
            inputs = self.get_inputs_from_workflow_step(workflow_step)

        initialised_inputs = self.setup_job_dataset_associations(inputs, io='inputs')
        return initialised_inputs

        
    def get_inputs_from_test(self, test_item=0) -> dict:
        return [
            'file_input'
        ]


    def get_inputs_from_workflow_step(self, workflow_step: Json) -> dict:
        pass


    def setup_job_dataset_associations(self, files: list[str], io: str='inputs') -> list[Union[JobToInputDatasetAssociation, JobToOutputDatasetAssociation]]:
        # TODO make this automated load from test case.
        # expand to allow load from workflow step later. 
        job_datasets = []
        for fname in files:
            i, path = self.dataset_counter, fname + '.dat'
            if io == 'inputs':
                assoc = JobToInputDatasetAssociation(name=fname, dataset=self.gen_hda(i, fname, path))
            elif io == 'outputs':
                assoc = JobToOutputDatasetAssociation(name=fname, dataset=self.gen_hda(i, fname, path))
            job_datasets.append(assoc)
            self.dataset_counter += 1

        return job_datasets


    def gen_hda(self, id, name, path) -> HistoryDatasetAssociation:
        hda = HistoryDatasetAssociation(name=name, metadata=dict())
        hda.dataset = Dataset(id=id, external_filename=path)
        hda.dataset.metadata = dict()
        hda.children = []
        self.app.model.context.add(hda)
        self.app.model.context.flush()

        return hda


    def setup_output_associations(self, workflow_step: Json=None) -> list[JobToOutputDatasetAssociation]:
        if workflow_step is None:
            outputs = self.get_outputs_from_test(test_item=0)
        else:
            outputs = self.get_outputs_from_workflow_step(workflow_step)

        initialised_outputs = self.setup_job_dataset_associations(outputs, io='outputs')
        return initialised_outputs

        
    def get_outputs_from_test(self, test_item=0) -> dict:
        return [
            'report'
        ]


    def get_outputs_from_workflow_step(self, workflow_step: Json) -> dict:
        pass

    
    def evaluate(self) -> None:
        self.set_compute_environment()
        command_line, _, __ = self.evaluator.build()

    
    def set_compute_environment(self, **kwds):
        kwds["working_directory"] = self.test_directory
        kwds["new_file_path"] = self.app.config.new_file_path
        self.evaluator.set_compute_environment(ComputeEnvironment(**kwds))
        #assert "exec_before_job" in self.tool.hooks_called





BWA_PARAMS = {
    "thresh": "4"
}
# these would usually be parsed from test cases or
# from the tool options in tha .ga workflow step
BWA_INPUTS = ['input1', 'input2']
BWA_OUTPUTS = ['output1']


ABRICATE_LIST_PARAMS = {}
ABRICATE_LIST_INPUTS = []
ABRICATE_LIST_OUTPUTS = ['report']

ABRICATE_PARAMS = {
    'file_input': ['hello.txt'],
    'adv': json.dumps({
        'db': 'resfinder',
        'no_header': False,
        'min_dna_id': 80,
        'min_cov': None,
    })
}

ABRICATE_INPUTS = ['file_input']
ABRICATE_OUTPUTS = ['report']


#TOOL_FILE = 'busco.xml'
#TOOL_DIR = 'busco'
TOOL_FILE = 'abricate.xml'
TOOL_DIR = 'tools/abricate'

JOB_SUCCESS = 0
JOB_FAIL = 0
    
def main():
    run_single_tool()
    #run_all_tools()


def run_single_tool():
    tmpl = Templator(TOOL_FILE, TOOL_DIR)
    tmpl.init_objects()
    tmpl.setup_job()
    tmpl.evaluate()


def run_all_tools():
    tools_folder = 'tools'
    tool_directories = get_directories(tools_folder)
    run(tools_folder, tool_directories)


def get_directories(folder_path):
    files = os.listdir(folder_path)
    directories = [f for f in files if os.path.isdir(f'{folder_path}/{f}')]
    return directories


def run(tools_folder, tool_directories) -> None:
    TH_COUNT = 10
    jobs = []

    # set up all jobs to complete
    for tool_dir in tool_directories:
        xmls = get_xmls(tools_folder, tool_dir)
        for xml in xmls:
            jobs.append([tools_folder, tool_dir, xml])

    # execute jobs using threads
    for i in range(0, len(jobs), TH_COUNT):
        threads = []

        for j in range(TH_COUNT):
            if i + j < len(jobs):
                job = jobs[i + j]
                t = threading.Thread(target=worker, args=(job,))
                t.daemon = True
                threads.append(t)

        for j in range(len(threads)):
            threads[j].start()

        for j in range(len(threads)):
            threads[j].join()
            

def get_xmls(workdir, tool_dir) -> list[str]:
    files = os.listdir(f'{workdir}/{tool_dir}')
    xmls = [f for f in files if f.endswith('xml')]
    xmls = [x for x in xmls if 'macros' not in x]
    return xmls


def worker(job: list[str]) -> None:
    try:
        tmpl = Templator(f'{job[2]}', f'{job[0]}/{job[1]}')
        tmpl.init_objects()
        print(f'success {job[1]}')
    except:
        print(f'fail {job[1]}')
    #tmpl.setup_job()
    #tmpl.evaluate()
    #print()


if __name__ == '__main__':
    main()






"""
def translate_ioparams_to_textparams(self, tool_source):
    root = tool_source.xml_tree.getroot()

    inputs_node = root.find('inputs')
    for node in inputs_node:
        self.translate_input_to_text(node)
    
    outputs_node = root.find('outputs')
    for node in outputs_node:
        self.translate_output_to_text(node)


    


    def init_compute_env(self) -> ComputeEnvironment:
        job_path_1 = '%s/dataset_1.dat' % self.test_directory
        job_path_2 = '%s/dataset_2.dat' % self.test_directory

        env = {}
        env['input_paths'] = [DatasetPath(1, '/galaxy/files/dataset_1.dat', false_path=job_path_1)]
        env['output_paths'] = [DatasetPath(2, '/galaxy/files/dataset_2.dat', false_path=job_path_2)]
        env['new_file_path'] = self.app.config.new_file_path
        env['working_directory'] = self.test_directory
        #env['tool_dir'] = self.tool_dir

        return ComputeEnvironment(**env)

    
"""