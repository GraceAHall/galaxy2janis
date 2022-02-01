

import sys
from typing import Container 


from execution import load_settings
from execution.settings import ExecutionSettings

from xml_ingestion import ingest
from tool.tool_definition import GalaxyToolDefinition

from command.Command import Command
from containers.Container import Container



# main entry point
def main():
    esettings = load_settings(sys.argv[1:])
    gx_tool_def = ingest_tool(esettings)
    command = infer_command(esettings, gx_tool_def)
    container = fetch_container(esettings, gx_tool_def)
    write_janis(esettings, gx_tool_def, command, container)
    write_tests(esettings, gx_tool_def)


def ingest_tool(esettings: ExecutionSettings) -> GalaxyToolDefinition:
    xml_path = esettings.get_xml_path()
    return ingest(xml_path, method='galaxy')


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






    

