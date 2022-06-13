



from typing import Any
from workflows.entities.step.metadata import StepMetadata
from galaxy_wrappers.wrappers.Wrapper import Wrapper
from galaxy_wrappers.wrappers.WrapperCache import WrapperCache
from galaxy_wrappers.requests.versions import request_installable_revision
import galaxy_wrappers.scraping.utils as utils


"""
This module parses a galaxy step (.ga format) and produces StepMetadata.
During the process it identifies which toolshed Wrapper will be used.

The Wrapper is an important part of StepMetadata. 
It contains information about the tool_id, tool_build, revision,
date_created, conda requirements etc

Local information about Wrappers is stored in data/wrappers/wrappers.json.
If information about which Wrapper to use is not available locally, 
API requests are made to the galaxy toolshed to determine the most suitable wrapper. 
its information is then known and saved to the json file. 

The WrapperCache class is responsible for presenting our local knowledgebank of
wrappers during this phase.
"""


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
    wrappers = get_local(gxstep)
    if not wrappers:
        wrappers = get_toolshed(gxstep)
    return most_recent(wrappers)
        
def get_local(gxstep: dict[str, Any]) -> list[Wrapper]:
    cache = WrapperCache(utils.WRAPPER_DATA_PATH)
    return cache.get(
        owner=gxstep['tool_shed_repository']['owner'],
        repo=gxstep['tool_shed_repository']['name'],
        tool_id=gxstep['tool_id'].rsplit('/', 2)[-2],
        tool_build=gxstep['tool_version']
    )

def get_toolshed(gxstep: dict[str, Any]) -> list[Wrapper]:
    # scrape toolshed for wrappers and update cache
    cache = WrapperCache(utils.WRAPPER_DATA_PATH)
    wrappers = request_installable_revision(gxstep)
    for wrapper in wrappers:
        cache.add(wrapper)
    # confirm can now load wrapper details from cache
    local_wrappers = get_local(gxstep)
    if not local_wrappers:
        raise RuntimeError()
    return local_wrappers

def most_recent(wrappers: list[Wrapper]) -> Wrapper:
    """return the most recent wrapper which matches [version]"""
    wrappers.sort(key=lambda x: x.date_created, reverse=True)
    return wrappers[0]

