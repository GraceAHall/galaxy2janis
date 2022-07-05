

import settings

from typing import Any
from gx.wrappers import fetch_wrapper
from utils.galaxy import get_xml_id
import utils.galaxy as utils


def tool_setup(args: dict[str, Any]) -> None:
    update_tool_settings(args)
    handle_wrapper_download()
    validate_tool_settings()

def update_tool_settings(args: dict[str, Any]) -> None:
    if args['local']:
        settings.tool.set_tool_path(args['local'])
        tool_id = get_xml_id(settings.tool.tool_path)
        assert(tool_id)
        settings.tool.set_tool_id(tool_id)
    if args['remote']:
        owner, repo, tool_id, revision = args['remote'].split(',')
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


### VALIDATION ###

def validate_tool_settings() -> None:
    # both local & remote params not given
    if not _has_xml() or not _valid_xml():
        raise RuntimeError('no valid xml file')

def _has_xml() -> bool:
    if settings.tool.tool_path:
        return True
    return False

def _valid_xml() -> bool:
    path = settings.tool.tool_path
    if utils.is_tool_xml(path):
        return True
    return False


