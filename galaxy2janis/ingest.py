

import json
from typing import Any
from galaxy2janis import settings
from galaxy2janis import mapping

from galaxy2janis.startup import tool_setup
from galaxy2janis.gx.gxtool import load_xmltool
from galaxy2janis.gx.command import gen_command
from galaxy2janis.containers import fetch_container

from galaxy2janis.entities.tool.generate import gen_tool
from galaxy2janis.entities.tool import Tool
from galaxy2janis.entities.workflow import Workflow
from galaxy2janis.entities.workflow import StepMetadata

from galaxy2janis.gx.gxworkflow.parsing.metadata import ingest_metadata
from galaxy2janis.gx.gxworkflow.parsing.inputs import ingest_workflow_inputs
from galaxy2janis.gx.gxworkflow.parsing.step import ingest_workflow_steps
from galaxy2janis.gx.gxworkflow.parsing.tool_step.prepost import ingest_workflow_steps_prepost
from galaxy2janis.gx.gxworkflow.parsing.tool_step.outputs import ingest_workflow_steps_outputs
from galaxy2janis.gx.gxworkflow.parsing.tool_state import load_tool_state

from galaxy2janis.gx.gxworkflow.values import handle_step_connection_inputs
from galaxy2janis.gx.gxworkflow.values import handle_step_runtime_inputs
from galaxy2janis.gx.gxworkflow.values import handle_step_static_inputs
from galaxy2janis.gx.gxworkflow.values import handle_step_default_inputs

from galaxy2janis.gx.gxworkflow.updates import update_component_knowledge
from galaxy2janis.gx.gxworkflow.connections import handle_scattering
from galaxy2janis.gx.gxworkflow.values.scripts import handle_step_script_inputs

from galaxy2janis.gx.wrappers.downloads.wrappers import get_builtin_tool_path

from galaxy2janis import datatypes

# TODO future 
# from galaxy2janis.gx.xmltool.tests import write_tests


def ingest_tool(path: str) -> Tool:
    """
    ingests a galaxy tool xml file into a galaxy2janis Tool (internal representation).
    'galaxy' is the galaxy tool representation, and
    'internal' is the internal tool representation we will build. 
    """
    datatypes.populate()
    settings.tool.tool_path = path
    galaxy = load_xmltool(path)
    command = gen_command(galaxy)
    container = fetch_container(galaxy.metadata.get_main_requirement())
    internal = gen_tool(galaxy, command, container)
    return internal

def ingest_workflow(path: str) -> Workflow:
    """
    ingests a galaxy workflow file into a galaxy2janis Workflow (internal representation).
    'galaxy' is the galaxy workflow representation, and
    'internal' is the internal workflow representation we will build. 
    order seems weird but trust me there is reason for this ordering.
    """
    datatypes.populate()
    galaxy = _load_galaxy_workflow(path)
    internal = Workflow()

    # ingesting workflow entities to internal
    ingest_metadata(internal, galaxy)
    ingest_workflow_inputs(internal, galaxy)
    ingest_workflow_steps(internal, galaxy)
    ingest_workflow_tools(internal, galaxy)
    ingest_workflow_steps_prepost(internal, galaxy)
    ingest_workflow_steps_outputs(internal, galaxy) 

    # assigning step input values
    handle_step_connection_inputs(internal, galaxy)
    handle_step_runtime_inputs(internal, galaxy)
    handle_step_script_inputs(internal)
    handle_step_static_inputs(internal, galaxy)
    handle_step_default_inputs(internal)

    # post ingestion tasks
    update_component_knowledge(internal)
    handle_scattering(internal)
    return internal

def ingest_workflow_tools(janis: Workflow, galaxy: dict[str, Any]) -> None:
    for g_step in galaxy['steps'].values():
        if g_step['type'] == 'tool':
            j_step = mapping.step(g_step['id'], janis, galaxy)
            tool = _parse_step_tool(j_step.metadata)
            j_step.set_tool(tool)
            g_step['tool_state'] = load_tool_state(g_step)


def _load_galaxy_workflow(path: str) -> dict[str, Any]:
    with open(path, 'r') as fp:
        return json.load(fp)

def _parse_step_tool(metadata: StepMetadata) -> Tool:
    args = _create_tool_settings_for_step(metadata)
    tool_setup(args)
    return ingest_tool(settings.tool.tool_path)

def _create_tool_settings_for_step(metadata: StepMetadata) -> dict[str, Any]:
    tool_id = metadata.wrapper.tool_id
    if metadata.wrapper.inbuilt:
        xml_path = get_builtin_tool_path(tool_id)
        assert(xml_path)
        return {
            'infile': xml_path,
            'remote': None,
            'outdir': None
            #'outdir': f'{paths.wrapper(tool_id, tool_id)}'
        }
    else:
        revision = metadata.wrapper.revision
        owner = metadata.wrapper.owner
        repo = metadata.wrapper.repo
        return {
            'infile': None,
            'remote': f'{owner},{repo},{tool_id},{revision}',
            'outdir': None
            #'outdir': f'{paths.wrapper(tool_id, revision)}'
        }
