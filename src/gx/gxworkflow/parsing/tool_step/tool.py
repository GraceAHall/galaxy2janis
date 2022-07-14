

from typing import Any

from entities.tool import Tool
from entities.workflow import StepMetadata
from entities.workflow import Workflow

from tool_mode import tool_mode
from gx.gxworkflow.parsing.tool_state import load_tool_state
from gx.interaction import get_builtin_tool_path

import mapping
import settings

def ingest_workflow_tools(janis: Workflow, galaxy: dict[str, Any]) -> None:
    for g_step in galaxy['steps'].values():
        if g_step['type'] == 'tool':
            j_step = mapping.step(g_step['id'], janis, galaxy)
            tool = parse_step_tool(j_step.metadata)
            j_step.set_tool(tool)
            g_step['tool_state'] = load_tool_state(g_step)

def parse_step_tool(metadata: StepMetadata) -> Tool:
    args = create_tool_settings_for_step(metadata)
    settings.tool.update(args)
    return tool_mode()

def create_tool_settings_for_step(metadata: StepMetadata) -> dict[str, Any]:
    tool_id = metadata.wrapper.tool_id
    if metadata.wrapper.inbuilt:
        xml_path = get_builtin_tool_path(tool_id)
        return {
            'local': xml_path,
            'remote': None,
            'outdir': None
            #'outdir': f'{paths.manager.wrapper(tool_id, tool_id)}'
        }
    else:
        revision = metadata.wrapper.revision
        owner = metadata.wrapper.owner
        repo = metadata.wrapper.repo
        return {
            'local': None,
            'remote': f'{owner},{repo},{tool_id},{revision}',
            'outdir': None
            #'outdir': f'{paths.manager.wrapper(tool_id, revision)}'
        }
