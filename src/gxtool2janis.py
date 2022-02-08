

import sys
from typing import Container

from runtime.startup import load_settings
from runtime.settings import ExecutionSettings

from gxmanager import GalaxyManager
from tool.parsing import parse_gx_to_internal
from tool.tool_definition import GalaxyToolDefinition

from command.Command import Command
from containers.Container import Container



# main entry point
def main():
    esettings: ExecutionSettings = load_settings(sys.argv[1:])
    gxmanager = load_galaxy_manager(esettings)
    toolrep = load_tool(gxmanager)
    

    command = infer_command(gxmanager, toolrep)

    container = fetch_container(esettings, toolrep)
    write_janis(esettings, toolrep, command, container)
    write_tests(esettings, toolrep)


def load_galaxy_manager(esettings: ExecutionSettings) -> GalaxyManager:
    return GalaxyManager(esettings.get_xml_path())

def load_tool(gxmanager: GalaxyManager) -> GalaxyToolDefinition:
    galaxytool = gxmanager.get_tool()
    return parse_gx_to_internal(galaxytool)

def infer_command(gxmanager: GalaxyManager, tooldef: GalaxyToolDefinition) -> Command:
    commandstrs = gxmanager.get_command_strings(tooldef)
    print()

def fetch_container(esettings: ExecutionSettings, tooldef: GalaxyToolDefinition) -> Container:
    pass

def write_janis(esettings: ExecutionSettings, 
                tooldef: GalaxyToolDefinition,
                command: Command, 
                container: Container) -> None:
    pass


def write_tests(esettings: ExecutionSettings, tooldef: GalaxyToolDefinition) -> None:
    pass



if __name__ == '__main__':
    main()






    

