

from typing import Any

import logs.logging as logging
import settings
import fileio
import paths

from paths import DEFAULT_TOOL_OUTDIR
from paths import DEFAULT_WORKFLOW_OUTDIR

def general_setup(args: dict[str, Any]) -> None:
    outdir = format_outdir(args)
    settings.general.set_command(args['command']) 
    paths.init_manager(settings.general.command, outdir)
    setup_file_structure()
    logging.configure_logging()

def format_outdir(args: dict[str, Any]) -> str:
    # user specified outdir
    if args['outdir']:
        return args['outdir']
    # auto formatted outdir
    else:
        parent_dir = auto_parent_dir(args)
        project_name = auto_project_name(args)
        return f'{parent_dir}/{project_name}'
    
def auto_parent_dir(args: dict[str, Any]) -> str:
    assert(args['outdir'] is None)
    match args['command']:
        case 'tool':
            return DEFAULT_TOOL_OUTDIR
        case 'workflow':
            return DEFAULT_WORKFLOW_OUTDIR
        case _:
            raise RuntimeError()

def auto_project_name(args: dict[str, Any]) -> str:
    match args['command']:
        case 'tool':
            return auto_tool_project_name(args)
        case 'workflow':
            return auto_workflow_project_name(args)
        case _:
            raise RuntimeError()

def auto_tool_project_name(args: dict[str, Any]) -> str:
    if args['local']:
        return args['local'].rsplit('/', 1)[-1].split('.', 1)[0]
    elif args['remote']:
        return args['remote'].split(',')[2]
    else:
        raise RuntimeError()

def auto_workflow_project_name(args: dict[str, Any]) -> str:
    return args['workflow'].rsplit('/', 1)[-1].split('.', 1)[0]

def setup_file_structure() -> None:
    project_dir = paths.manager.project_dir()
    fileio.init_folder(project_dir)
    for subfolder in paths.manager.subfolders():
        fileio.init_folder(f'{project_dir}/{subfolder}')



"""

file structure initialisation

tool mode
- outdir
- janis.log
- messages.log

workflow mode
- outdir
- janis.log
- messages.log
- each item in paths.manager.folder_structure

"""