
import logs.logging as logging
from typing import Any

import settings.tool.settings as tsettings
from settings.tool.validation import validate_tool_settings
from gx.wrappers.downloads.wrappers import fetch_wrapper

from gx.xmltool.load import load_xmltool
from shellparser.command import gen_command
from containers.containers import fetch_container
from entities.tool.generate import gen_tool
from entities.tool.Tool import Tool

# TODO future 
# from gx.xmltool.tests import write_tests

"""
this file parses a single tool to janis
the steps involved are laid out in order
each step involves a single module
"""

def tool_mode(args: dict[str, Any]) -> Tool:
    # main 
    startup(args)
    xmltool = load_xmltool()
    command = gen_command(xmltool)
    container = fetch_container(xmltool)
    tool = gen_tool(xmltool, command, container)
    return tool


def startup(args: dict[str, Any]) -> None:
    update_tool_settings(args)
    validate_tool_settings()
    handle_wrapper_download()
    update_logging()

def update_tool_settings(args: dict[str, Any]) -> None:
    if args['local']:
        tsettings.set_tool_path(args['local'])
    if args['remote']:
        owner, repo, tool_id, revision = args['remote'].split()
        revision = revision.rsplit(':', 1)[-1] # incase numeric:revision
        tsettings.set_owner(owner)
        tsettings.set_repo(repo)
        tsettings.set_tool_id(tool_id)
        tsettings.set_revision(revision)
    tsettings.set_dev_test_cmdstrs(value=args['dev_test_cmdstrs'])

def handle_wrapper_download() -> None:
    # if remote download, download wrapper, cache, return path
    if tsettings.owner and tsettings.repo and tsettings.revision and tsettings.tool_id:
        path = fetch_wrapper(
            tsettings.owner,
            tsettings.repo,
            tsettings.revision,
            tsettings.tool_id
        )
        tsettings.set_tool_path(path)

def update_logging() -> None:  
    logging.configure_tool_logging()
    logging.msg_parsing_tool()