

import sys
from typing import Optional

from runtime.startup import load_settings, ExecutionSettings
from galaxy_interaction import load_manager, GalaxyManager
from tool.tool import load_tool, GalaxyToolDefinition
from tool.tests import write_tests
from command.infer import infer_command, Command
from containers.fetch import fetch_container, Container
from janis.write_definition import write_janis

"""
this file contains the main function for gxtool2janis
the steps involved are laid out in order
each step involves a single module
only the tool module is called twice (load_tool, and write_tests)
"""


def main():
    # main entry point
    esettings: ExecutionSettings = load_settings(sys.argv[1:])
    gxmanager: GalaxyManager = load_manager(esettings)
    tool: GalaxyToolDefinition = load_tool(gxmanager)
    command: Command = infer_command(gxmanager, tool)
    container: Optional[Container] = fetch_container(esettings, tool)
    write_janis(esettings, tool, command, container)
    write_tests(esettings, tool)


if __name__ == '__main__':
    main()






    

