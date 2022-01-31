

import sys
from typing import Container 


from classes.execution import startup
from classes.execution.settings import ExecutionSettings
from classes.tool.GalaxyToolDefinition import GalaxyToolDefinition
from classes.command.Command import Command
from classes.containers.Container import Container



# main entry point
def main():
    esettings = startup(sys.argv[1:])
    gx_tool_def = load_tool(esettings)
    command = infer_command(esettings, gx_tool_def)
    container = fetch_container(esettings, gx_tool_def)
    write_janis(esettings, gx_tool_def, command, container)
    write_tests(esettings, gx_tool_def)


def load_tool(esettings: ExecutionSettings) -> GalaxyToolDefinition:
    xml_path = esettings.get_xml_path()
    return GalaxyToolDefinition(xml_path)


def infer_command(esettings: ExecutionSettings, gx_tool_def: GalaxyToolDefinition) -> Command:
    pass


def fetch_container(esettings: ExecutionSettings, gx_tool_def: GalaxyToolDefinition) -> Container:
    pass


def write_janis(esettings: ExecutionSettings, 
                gx_tool_def: GalaxyToolDefinition,
                command: Command, 
                container: Container) -> None:
    pass


def write_tests(esettings: ExecutionSettings, gx_tool_def: GalaxyToolDefinition) -> None:
    pass



if __name__ == '__main__':
    main()






    

