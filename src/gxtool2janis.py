
#sys.path.append('./galaxy/lib')

import logs.logging as logging

import sys
from typing import Any, Optional

import settings
import paths

from cli import CLIparser
from tool_mode import tool_mode
from workflow_mode import workflow_mode
from fileio import write_tool

"""
gxtool2janis program entry point
parses cli settings then hands execution to other files based on command
"""

def main():
    logging.configure_warnings()
    args = load_args()
    run_sub_program(args)

def load_args() -> dict[str, Optional[str]]:
    args = CLIparser(sys.argv).args
    set_general_settings(args)
    return args

def set_general_settings(args: dict[str, Any] ) -> None:
    settings.general.set_command(args['command']) 
    settings.general.set_outdir(args['outdir'])
    settings.general.set_dev_test_cmdstrs(args['dev_test_cmdstrs'])
    paths.init_manager(settings.general.command)

def run_sub_program(args: dict[str, Optional[str]]) -> None:
    match args['command']:
        case 'tool':
            run_tool_mode(args)
            #try_run_tool_mode(args)
        case 'workflow':
            run_workflow_mode(args)
            #try_run_workflow_mode(args)
        case _:
            pass

def run_tool_mode(args: dict[str, Optional[str]]):
    tool = tool_mode(args)
    write_tool(tool)  # I dont like this design, but it may be necessary

def run_workflow_mode(args: dict[str, Optional[str]]):
    workflow_mode(args)


# for bulk parsing stat runs

def try_run_tool_mode(args: dict[str, Optional[str]]):
    try: 
        tool = tool_mode(args)
        write_tool(tool)
    except Exception as e:
        print(e)
        logging.tool_exception()

def try_run_workflow_mode(args: dict[str, Optional[str]]):
    try: 
        workflow_mode(args)
    except Exception as e:
        print(e)
        logging.workflow_exception()
    

if __name__ == '__main__':
    main()
