


import os 
from typing import Tuple 

from entities.workflow.step.metadata import StepMetadata
import gx.utils.general_utils as utils


def get_builtin_tool_path(metadata: StepMetadata) -> Tuple[str, str]:
    tool_directories = _get_builtin_tool_directories()
    for directory in tool_directories:
        xmlfile = utils.get_xmlfile_by_tool_id(directory, metadata.wrapper.tool_id)
        if xmlfile:
            return directory, xmlfile
    raise RuntimeError(f'cannot locate builtin tool {metadata.wrapper.tool_id}') 

def _get_builtin_tool_directories() -> list[str]:
    out: list[str] = []
    out += _get_builtin_tools_directories()
    out += _get_datatype_converter_directories()
    return out

def _get_builtin_tools_directories() -> list[str]:
    import galaxy_src.tools
    tools_folder = str(galaxy_src.tools.__file__).rsplit('/', 1)[0]
    bundled_folders = os.listdir(f'{tools_folder}/bundled')
    bundled_folders = [f for f in bundled_folders if not f.startswith('__')]
    bundled_folders = [f'{tools_folder}/bundled/{f}' for f in bundled_folders]
    bundled_folders = [f for f in bundled_folders if os.path.isdir(f)]
    return [tools_folder] + bundled_folders

def _get_datatype_converter_directories() -> list[str]:
    import galaxy_src.datatypes
    datatypes_folder = str(galaxy_src.datatypes.__file__).rsplit('/', 1)[0]
    converters_folder = f'{datatypes_folder}/converters'
    return [converters_folder]
