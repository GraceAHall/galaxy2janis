
import runtime.logging.logging as logging
from runtime.settings.ExeSettings import ToolExeSettings
from xmltool.load import load_xmltool
from command.command import gen_command
from containers.fetch import fetch_container
from tool.generate import gen_tool

# TODO future 
#from xmltool.tests import write_tests


"""
this file parses a single tool to janis
the steps involved are laid out in order
each step involves a single module
only the tool module is called twice (load_tool, and write_tests)
"""

def tool_mode(esettings: ToolExeSettings):
    assert(esettings.xmlfile)
    logging.configure_tool_logging(esettings)
    logging.msg_parsing_tool(esettings.xmlfile)
    xmltool = load_xmltool(esettings)
    command = gen_command(esettings, xmltool)
    container = fetch_container(esettings, xmltool)
    tool = gen_tool(xmltool, command, container)
    return tool
