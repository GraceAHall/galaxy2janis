
#sys.path.append('./galaxy/lib')

import logs.logging as logging

import sys
import fileio

from typing import Optional

from setup import general_setup
from cli import CLIparser
from tool_mode import tool_mode
from workflow_mode import workflow_mode

import paths
import settings

"""
gxtool2janis program entry point
parses cli settings then hands execution to other files based on command
"""

def main():
    logging.configure_warnings()
    args = load_args()
    general_setup(args)
    run_sub_program(args)

def load_args() -> dict[str, Optional[str]]:
    cli = CLIparser(sys.argv)
    return cli.args

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
    settings.tool.set(args)
    tool = tool_mode()
    path = paths.manager.tool(tool.metadata.id)
    fileio.write_tool(tool, path=path)  # I dont like this design, but it may be necessary

def run_workflow_mode(args: dict[str, Optional[str]]):
    workflow_mode(args)


# for bulk parsing stat runs

def try_run_tool_mode(args: dict[str, Optional[str]]):
    try: 
        run_tool_mode(args)
    except Exception as e:
        # print('\n####################')
        # print(settings.tool.tool_id.upper())
        # print('####################\n')
        # print()
        print(e)
        logging.tool_exception()

def try_run_workflow_mode(args: dict[str, Optional[str]]):
    try: 
        run_workflow_mode(args)
    except Exception as e:
        print(e)
        logging.workflow_exception()
    

if __name__ == '__main__':
    main()
