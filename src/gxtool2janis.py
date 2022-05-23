
#sys.path.append('./galaxy/lib')

import runtime.logging.logging as logging
import sys

from typing import Optional
from startup.CLIparser import CLIparser

from parse_tool import parse_tool
from parse_workflow import parse_workflow
from runtime.settings.settings import load_tool_settings, load_workflow_settings
from runtime.settings.ExeSettings import ToolExeSettings, WorkflowExeSettings
from file_io.write import write_tool, write_workflow

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
            #run_tool_mode(args)
            try_run_tool_mode(args)
        case 'workflow':
            #run_workflow_mode(args)
            try_run_workflow_mode(args)
        case _:
            pass

def run_tool_mode(args: dict[str, Optional[str]]):
    esettings: ToolExeSettings = load_tool_settings(args)
    tool = parse_tool(esettings)
    write_tool(esettings, tool)

def try_run_tool_mode(args: dict[str, Optional[str]]):
    esettings: ToolExeSettings = load_tool_settings(args)
    try: 
        tool = parse_tool(esettings)
        write_tool(esettings, tool)
    except Exception as e:
        logging.tool_exception()
        print(e)

def run_workflow_mode(args: dict[str, Optional[str]]):
    esettings: WorkflowExeSettings = load_workflow_settings(args)
    workflow = parse_workflow(esettings)
    write_workflow(esettings, workflow)

def try_run_workflow_mode(args: dict[str, Optional[str]]):
    esettings: WorkflowExeSettings = load_workflow_settings(args)
    try: 
        workflow = parse_workflow(esettings)
        write_workflow(esettings, workflow)
    except Exception as e:
        logging.workflow_exception()
        print(e)
    

if __name__ == '__main__':
    main()
