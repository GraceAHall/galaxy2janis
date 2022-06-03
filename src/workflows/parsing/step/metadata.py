



from typing import Any
from workflows.entities.step.metadata import StepMetadata
from galaxy_wrappers.wrappers.Wrapper import Wrapper
from galaxy_wrappers.wrappers.WrapperCache import WrapperCache
from galaxy_wrappers.scraping.single import scrape_single_repo
import galaxy_wrappers.scraping.utils as utils


def parse_step_metadata(gxstep: dict[str, Any]) -> StepMetadata:
    return StepMetadata(
        wrapper=get_wrapper(gxstep),
        uuid=gxstep['uuid'],
        step_id=gxstep['id'],
        step_name=gxstep['name'],
        tool_state=gxstep['tool_state'], 
        workflow_outputs=gxstep['workflow_outputs'],
        label=gxstep['label']
    )

def get_wrapper(gxstep: dict[str, Any]) -> Wrapper:
    if 'tool_shed_repository' not in gxstep:
        return get_wrapper_builtin(gxstep)
    else:
        return get_wrapper_toolshed(gxstep)

def get_wrapper_builtin(gxstep: dict[str, Any]) -> Wrapper:
    raise NotImplementedError()

def get_wrapper_toolshed(gxstep: dict[str, Any]) -> Wrapper:
    wrappers = get_local_wrappers(gxstep)
    if not wrappers:
        wrappers = get_toolshed_wrappers(gxstep)
    return most_recent(wrappers)
        
def get_local_wrappers(gxstep: dict[str, Any]) -> list[Wrapper]:
    owner, repo, tool_id, tool_version = gxstep['tool_id'].split('/')[2:6]
    cache = WrapperCache(utils.WRAPPER_DATA_PATH)
    return cache.get(
        owner=owner,
        repo=repo,
        tool_id=tool_id,
        tool_version=tool_version
    )

def get_toolshed_wrappers(gxstep: dict[str, Any]) -> list[Wrapper]:
    # scrape toolshed for wrappers and update cache
    scrape_single_repo(
        owner=gxstep['tool_shed_repository']['owner'],
        repo=gxstep['tool_shed_repository']['name']
    )
    # confirm can now load wrapper details from cache
    local_wrappers = get_local_wrappers(gxstep)
    if not local_wrappers:
        raise RuntimeError()
    return local_wrappers

def most_recent(wrappers: list[Wrapper]) -> Wrapper:
    """return the most recent wrapper which matches [version]"""
    wrappers.sort(key=lambda x: x.date_created, reverse=True)
    return wrappers[0]

