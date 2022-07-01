

import settings

from typing import Any
from gx.wrappers import fetch_wrapper
from utils.galaxy import get_xml_id


def tool_setup(args: dict[str, Any]) -> None:
    update_tool_settings(args)
    handle_wrapper_download()
    settings.validation.validate_tool_settings()

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


