

from typing import Any

from entities.tool import Tool
from entities.workflow import StepMetadata
from entities.workflow import Workflow

from tool_mode import tool_mode
from gx.interaction import get_builtin_tool_path

import paths


def ingest_workflow_tools(janis: Workflow) -> None:
    for step in janis.steps:
        tool = parse_step_tool(step.metadata)
        step.set_tool(tool)

def parse_step_tool(metadata: StepMetadata) -> Tool:
    args = create_tool_settings_for_step(metadata)
    return tool_mode(args)

def create_tool_settings_for_step(metadata: StepMetadata) -> dict[str, Any]:
    if metadata.wrapper.inbuilt:
        xml_path = get_builtin_tool_path(metadata.wrapper.tool_id)
        return {
            'local': xml_path,
            'remote': None,
            'outdir': f'{paths.manager.wrapper(metadata)}'
        }
    else:
        owner = metadata.wrapper.owner
        repo = metadata.wrapper.repo
        tool_id = metadata.wrapper.tool_id
        revision = metadata.wrapper.revision
        return {
            'local': None,
            'remote': f'{owner},{repo},{tool_id},{revision}',
            'outdir': f'{paths.manager.wrapper(metadata)}'
        }
