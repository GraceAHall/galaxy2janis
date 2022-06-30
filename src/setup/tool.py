
import logs.logging as logging
from typing import Any

from gx.wrappers import fetch_wrapper
from utils.galaxy import get_xml_id

import settings
import fileio
import paths

def do_tool_setup(args: dict[str, Any]) -> None:
    update_tool_settings(args)
    settings.validation.validate_tool_settings()
    handle_wrapper_download()
    setup_file_structure()
    update_logging()

def update_tool_settings(args: dict[str, Any]) -> None:
    if args['local']:
        settings.tool.set_tool_path(args['local'])
        tool_id = get_xml_id(settings.tool.tool_path)
        assert(tool_id)
        settings.tool.set_tool_id(tool_id)
    if args['remote']:
        owner, repo, tool_id, revision = args['remote'].split()
        revision = revision.rsplit(':', 1)[-1] # incase numeric:revision
        settings.tool.set_owner(owner)
        settings.tool.set_repo(repo)
        settings.tool.set_tool_id(tool_id)
        settings.tool.set_revision(revision)

def handle_wrapper_download() -> None:
    # if remote download, download wrapper, cache, return path
    if settings.tool.owner and settings.tool.repo and settings.tool.revision and settings.tool.tool_id:
        path = fetch_wrapper(
            settings.tool.owner,
            settings.tool.repo,
            settings.tool.revision,
            settings.tool.tool_id
        )
        settings.tool.set_tool_path(path)

def setup_file_structure() -> None:
    if settings.general.command == 'tool':
        tool_def_path = paths.manager.tool()
        fileio.init_file(tool_def_path)

def update_logging() -> None:  
    logging.configure_tool_logging()
    logging.msg_parsing_tool()


"""

file structure initialisation

tool mode
- outdir
- janis.log
- messages.log

workflow mode
- outdir
- janis.log
- messages.log
- each item in paths.manager.folder_structure

"""