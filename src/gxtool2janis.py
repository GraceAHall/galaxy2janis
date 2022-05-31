
#sys.path.append('./galaxy/lib')

import runtime.logging.logging as logging
import sys

from typing import Optional
from startup.CLIparser import CLIparser

from tool_mode import tool_mode
from workflow_mode import workflow_mode
from runtime.settings.settings import load_tool_settings, load_workflow_settings
from runtime.settings.ExeSettings import ToolExeSettings, WorkflowExeSettings

"""
gxtool2janis program entry point
parses cli settings then hands execution to other files based on command
"""

def main():
    logging.configure_warnings()
    args = load_args()
    run_sub_program(args)

def load_args() -> dict[str, Optional[str]]:
    parser = CLIparser(sys.argv)
    return parser.args

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
    esettings: ToolExeSettings = load_tool_settings(args)
    tool_mode(esettings)

def try_run_tool_mode(args: dict[str, Optional[str]]):
    try: 
        esettings: ToolExeSettings = load_tool_settings(args)
        tool_mode(esettings)
    except Exception as e:
        print(e)
        logging.tool_exception()

def run_workflow_mode(args: dict[str, Optional[str]]):
    esettings: WorkflowExeSettings = load_workflow_settings(args)
    workflow_mode(esettings)

def try_run_workflow_mode(args: dict[str, Optional[str]]):
    try: 
        esettings: WorkflowExeSettings = load_workflow_settings(args)
        workflow_mode(esettings)
    except Exception as e:
        print(e)
        logging.workflow_exception()
    

if __name__ == '__main__':
    main()
