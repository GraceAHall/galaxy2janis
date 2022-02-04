

from typing import Any

import regex as re

from galaxy.tool_util.parser.output_objects import ToolOutput
from galaxy_tool.param.ParamRegister import ParamRegister 




### OUTPUT FUNCTIONS

def is_tool_output(gxobj: Any) -> bool:
    if isinstance(gxobj, ToolOutput):
        return True
    elif issubclass(type(gxobj), ToolOutput):
        return True
    return False



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





