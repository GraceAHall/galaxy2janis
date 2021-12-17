


from collections import Counter
from typing import Optional, Union, Any
import regex as re
from classes.params.ParamRegister import ParamRegister 

from classes.templating.MockClasses import MockApp, ComputeEnvironment
from galaxy.tool_util.parser.output_collection_def import FilePatternDatasetCollectionDescription
from galaxy.tool_util.parser.output_objects import ToolOutput
from galaxy.tools import Tool as GalaxyTool
from galaxy.tools.evaluation import ToolEvaluator
from galaxy.model import (
    Job,
    Dataset,
    HistoryDatasetAssociation,
    JobToInputDatasetAssociation,
    JobToOutputDatasetAssociation,
)
from galaxy.tools.parameters.basic import ToolParameter



## GALAXY TOOL EVALUATION ENGINE

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




### CLASS STUFF


def is_tool_parameter(gxobj: Any) -> bool:
    if type(gxobj) == ToolParameter:
        return True
    elif issubclass(type(gxobj), ToolParameter):
        return True
    return False


def is_tool_output(gxobj: Any) -> bool:
    if type(gxobj) == ToolOutput:
        return True
    elif issubclass(type(gxobj), ToolOutput):
        return True
    return False



### PARAM FUNCTIONS 

def get_param_formats(param: ToolParameter) -> list[str]:
    if param.formats:
        return [f.file_ext for f in param.formats]
    
    return []


def get_param_values(param: ToolParameter) -> list[str]:
    if param.type in ['select', 'boolean']:
        return get_param_options(param)
    
    elif param.type not in ['data', 'data_collection']:
        if param.value:
            return [param.value]
        
    return []

       
def get_param_options(param: ToolParameter) -> list[str]:
    """this works for select AND boolean params"""
    return param.legal_values


def get_param_default_value(param: ToolParameter) -> Optional[str]:
    if hasattr(param, 'value') and param.value is not None:
        return param.value
    
    elif param.type in ['select', 'boolean']:
        return get_param_primary_option(param)

    elif param.type in ['data', 'data_collection']:
        if len(param.formats) > 0:
            ext = param.formats[0].file_ext
            return param.name + '.' + ext

    elif param.type in ['integer', 'float']:
        if param.min:
            return param.min
        elif param.max:
            return param.max

    return None


def get_param_primary_option(param: ToolParameter) -> Optional[str]:
    # select params
    if param.type == 'select':
        for opt in param.static_options:
            if opt[2] == True:
                return opt[1]
        return param.static_options[0][1]
    
    # boolean params
    elif param.type == 'boolean':
        if hasattr(param, 'checked'):
            if param.checked == 'false':
                return param.falsevalue
            return param.truevalue
        
        else:
            if param.truevalue and param.truevalue != '':
                return param.falsevalue
            return param.truevalue

    return None


def get_output_dataset_collector(output: ToolOutput) -> Optional[FilePatternDatasetCollectionDescription]:
    if hasattr(output, 'dataset_collector_descriptions'):
        if output.dataset_collector_descriptions:
            return output.dataset_collector_descriptions[0]
    return None


def param_is_optional(param: ToolParameter) -> bool:
    # optionality explicitly set as true in param
    if param.optional:
        return True
    # param values include a blank string
    if '' in get_param_values(param):
        return True
    
    return False


def param_is_array(param: ToolParameter) -> bool:
    if param.type == 'data_collection':
        return True
    elif param.type == 'data' and param.multiple:
        return True
        
    return False



### OUTPUT FUNCTIONS

def output_is_optional(output: ToolOutput) -> bool:    
    return False


def output_is_array(output: ToolOutput) -> bool:    
    return False


def get_output_formats(output: ToolOutput, param_register: ParamRegister) -> list[str]:
    """
    DATATYPE ATTRIBUTES
    data|collection.discover_datasets.format
    data|collection.discover_datasets.ext
    """
    # this node contains info
    if hasattr(output, 'auto_format') and output.auto_format:
        return ['file']
    elif hasattr(output, 'format') and output.format:
        return output.format.split(',')
    
    # external param contains info
    elif hasattr(output, 'format_source') and output.format_source:
        __, source_param = param_register.get(output.format_source, allow_lca=True)
        return get_param_formats(source_param)

    # child node contains info (discover datasets)
    collector = get_output_dataset_collector(output)
    if collector and collector.default_ext:
        return collector.default_ext.split(',')
    
    # fallback
    return ['file']


def get_output_selector(output: ToolOutput) -> str:
    """
    returns the selector type based on the supplied output
    can be 'WildcardSelector' or 'InputSelector'
    """
    # data output
    if output.output_type == 'data':
        if output.from_work_dir or len(output.output_discover_patterns) > 0:
            return 'WildcardSelector'
    
    # collection output
    elif output.output_type == 'collection':
        return 'WildcardSelector'
        # NOTE - add support for the following later:
        # defined output elems in collection
        # structured_like=""

    return 'InputSelector'


def get_output_files_path(output: ToolOutput) -> str:
    """gets path to the files this output will collect"""   
    # defined in this node
    if hasattr(output, 'from_work_dir') and output.from_work_dir:
        return output.from_work_dir
    
    # defined in child node
    collector = get_output_dataset_collector(output)
    if collector:
        directory = collector.directory or ''
        pattern = transform_discover_pattern(collector.discover_patterns[0])
        return f'{directory}/{pattern}'
    
    raise Exception('output has no files path')
    

def transform_discover_pattern(pattern: str) -> str:
    transformer = {
        '__designation__': '*',
        '.*?': '*',
        '\\.': '.',
    }

    # # remove anything in brackets
    # pattern_list = pattern.split('(?P<designation>')
    # if len(pattern_list) == 2:
    #     pattern_list[1] = pattern_list[1].split(')', 1)[-1]

    # find anything in between brackets
    bracket_strings = re.findall("\\((.*?)\\)", pattern)

    # remove brackets & anything previously found (lazy)
    pattern = pattern.replace('(', '').replace(')', '')
    for the_string in bracket_strings:
        if '<ext>' in the_string:
            pattern = pattern.replace(the_string, '') # lazy and bad
        pattern = pattern.replace(the_string, '*')

    for key, val in transformer.items():
        pattern = pattern.replace(key, val)

    # remove regex start and end patterns
    pattern = pattern.rstrip('$').lstrip('^')
    return pattern


def get_output_default_value(output: ToolOutput) -> str:
    ext = output.format.split(',')[0]
    return output.name + '.' + ext












