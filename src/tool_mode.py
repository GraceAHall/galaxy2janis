
from typing import Any

from setup import do_tool_setup
from gx.xmltool.load import load_xmltool

from shellparser.command import gen_command
from containers import fetch_container
from entities.tool.generate import gen_tool
from entities.tool import Tool

# TODO future 
# from gx.xmltool.tests import write_tests

"""
this file parses a single tool to janis
the steps involved are laid out in order
each step involves a single module
"""

def tool_mode(args: dict[str, Any]) -> Tool:
    do_tool_setup(args)
    xmltool = load_xmltool()
    command = gen_command(xmltool)
    container = fetch_container(xmltool.metadata.get_main_requirement())
    tool = gen_tool(xmltool, command, container)
    return tool

