



from runtime.Logger import Logger

from typing import Optional


from galaxy_interaction import load_manager, GalaxyManager
from startup.ExeSettings import ToolExeSettings
from xmltool.load import load_xmltool, XMLToolDefinition
#from xmltool.tests import write_tests
from command.infer import infer_command, Command
from containers.fetch import fetch_container, Container
from tool.Tool import Tool
from tool.generate import generate_tool


"""
this file parses a single tool to janis
the steps involved are laid out in order
each step involves a single module
only the tool module is called twice (load_tool, and write_tests)
"""

def parse_tool(esettings: ToolExeSettings):
    logger = Logger(esettings.get_logfile_path())
    # try:
    gxmanager: GalaxyManager = load_manager(esettings)
    xmltool: XMLToolDefinition = load_xmltool(gxmanager)
    command: Command = infer_command(gxmanager, xmltool)
    container: Optional[Container] = fetch_container(esettings, logger, xmltool)
    tool: Tool = generate_tool(xmltool, command, container)
    tool.register_component_tags()
    return tool
    # except Exception as e:
    #     print(e)
    #     logger.log(2, 'parse_tool failed')
        


    

