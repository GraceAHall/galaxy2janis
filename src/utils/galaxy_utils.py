


from collections import Counter
from typing import Union

from classes.templating.MockClasses import MockApp, ComputeEnvironment
from galaxy.tools import Tool as GalaxyTool
from galaxy.tools.evaluation import ToolEvaluator
from galaxy.model import (
    Job,
    Dataset,
    HistoryDatasetAssociation,
    JobToInputDatasetAssociation,
    JobToOutputDatasetAssociation,
)

## galaxy engine - tool evaluation 

def generate_dataset(app: MockApp, varname: str, iotype: str) -> Union[JobToInputDatasetAssociation, JobToOutputDatasetAssociation]:
    """
    creates a dataset association. 
    this process creates a dataset and updates the sql database model.
    """
    i = app.dataset_counter
    path = varname
    varrep = '__gxvar_' + varname
    app.dataset_counter += 1

    if iotype == 'input':
        return JobToInputDatasetAssociation(name=varname, dataset=generate_hda(app, i, path, varrep))
    elif iotype == 'output':
        return JobToOutputDatasetAssociation(name=varname, dataset=generate_hda(app, i, path, varrep))


def generate_hda(app: MockApp, id: int, name: str, path: str) -> HistoryDatasetAssociation:
    hda = HistoryDatasetAssociation(name=name, metadata=dict())
    hda.dataset = Dataset(id=id, external_filename=path)
    hda.dataset.metadata = dict()
    hda.children = []
    app.model.context.add(hda)
    app.model.context.flush()
    return hda


def setup_evaluator(app: MockApp, gxtool: GalaxyTool, job: Job, test_directory: str) -> ToolEvaluator:
    evaluator = ToolEvaluator(app, gxtool, job, test_directory)
    kwds = {}
    kwds["working_directory"] = test_directory
    kwds["new_file_path"] = app.config.new_file_path
    evaluator.set_compute_environment(ComputeEnvironment(**kwds))
    return evaluator



# ---- consolidating types ---- #

# TODO write tests for all these
type_consolidator = {
    'fastqsanger': 'fastq',
    'fastqsanger.gz': 'fastq.gz',
    'tabular': 'tsv',
}

def consolidate_types(types: str) -> str:
    # standardises types. ie fastq,fastqsanger -> fastq
    out_types: set[str] = set()

    type_list = types.split(',')
    for old_type in type_list:
        old_type = old_type.replace('\n', '').strip(' ')
        try:
            new_type = type_consolidator[old_type]
            out_types.add(new_type)
        except KeyError:
            out_types.add(old_type)
    
    out_types = list(out_types)
    out_types.sort(key=lambda x: len(x))
    return ','.join(out_types)


# ---- list operations ---- #
















