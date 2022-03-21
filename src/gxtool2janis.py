
#sys.path.append('./galaxy/lib')

import sys
from typing import Optional
from startup.CLIparser import CLIparser

from parse_tool import parse_tool
from parse_workflow import parse_workflow
from startup.settings import load_tool_settings
from startup.ExeSettings import ToolExeSettings
from startup.settings import load_workflow_settings
from startup.ExeSettings import WorkflowExeSettings
from janis.write_definition import write_definition
"""
gxtool2janis program entry point
parses cli settings then hands execution to other files based on command
"""


def main():
    args = load_args()
    match args['command']:
        case 'tool':
            run_tool_mode(args)
        case 'workflow':
            run_workflow_mode(args)
        case _:
            pass

def load_args() -> dict[str, Optional[str]]:
    parser = CLIparser(sys.argv)
    return parser.args

def run_tool_mode(args: dict[str, Optional[str]]):
    esettings: ToolExeSettings = load_tool_settings(args) 
    tool = parse_tool(esettings)
    write_definition(esettings.get_janis_definition_path(), tool)

def run_workflow_mode(args: dict[str, Optional[str]]):
    esettings: WorkflowExeSettings = load_workflow_settings(args)
    workflow = parse_workflow(esettings)
    print()


if __name__ == '__main__':
    main()






    

