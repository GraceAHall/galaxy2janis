
#sys.path.append('./galaxy/lib')

import sys
from typing import Optional
from startup.CLIparser import CLIparser

from parse_tool import parse_tool
from parse_workflow import parse_workflow


"""
gxtool2janis program entry point
parses cli settings then hands execution to other files based on command
"""


def main():
    args = load_args()
    match args['command']:
        case 'tool':
            parse_tool(args)
        case 'workflow':
            parse_workflow(args)
        case _:
            pass

def load_args() -> dict[str, Optional[str]]:
    parser = CLIparser(sys.argv)
    return parser.args


if __name__ == '__main__':
    main()






    

