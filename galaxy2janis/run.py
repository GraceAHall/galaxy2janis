

from galaxy2janis import aliases # leave at top
from galaxy2janis import settings
from typing import Optional

from galaxy2janis.startup import general_setup
from galaxy2janis.cli import CLIparser
from galaxy2janis import paths

from galaxy2janis.startup import tool_setup
from galaxy2janis.startup import workflow_setup
from galaxy2janis.ingest import ingest_tool
from galaxy2janis.ingest import ingest_workflow

from galaxy2janis.fileio import write_workflow
from galaxy2janis.fileio import write_tool


import sys


"""
gxtool2janis program entry point
parses cli settings then hands execution to other files based on command
"""


def main():
    args = CLIparser(sys.argv).args
    general_setup(args)

    if args['command'] == 'tool':
        tool_mode(args)
    elif args['command'] == 'workflow':
        workflow_mode(args)


def tool_mode(args: dict[str, Optional[str]]) -> None:
    tool_setup(args)
    tool = ingest_tool(settings.tool.tool_path)
    path = paths.tool(tool.metadata.id)
    write_tool(tool, path=path) 

def workflow_mode(args: dict[str, Optional[str]]) -> None:
    workflow_setup(args)
    wf = ingest_workflow(settings.workflow.workflow_path)
    write_workflow(wf)


if __name__ == '__main__':
    main()
