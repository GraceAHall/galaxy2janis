

from typing import Optional, Tuple 
import os

from startup.settings import load_tool_settings
from startup.ExeSettings import ToolExeSettings
from startup.ExeSettings import WorkflowExeSettings
from workflows.step.metadata.StepMetadata import StepMetadata
from workflows.workflow.Workflow import Workflow
import utils.etree as etree_utils 


def get_tool_settings(wsettings: WorkflowExeSettings, metadata: StepMetadata) -> ToolExeSettings:
    """generates ToolExeSettings for each tool to be parsed"""
    args = make_parse_tool_args(metadata, wsettings)
    return load_tool_settings(metadata, args)
        
def make_parse_tool_args(metadata: StepMetadata, esettings: WorkflowExeSettings) -> dict[str, Optional[str]]:
    if metadata.is_inbuilt:
        tool_dir, xml_filename = get_builtin_tool_path(metadata)
        return {
            'dir': tool_dir,
            'xml': xml_filename,
            'remote_url': None,
            'download_dir': None,
            'outdir': f'{esettings.get_janis_tools_dir()}/{metadata.tool_id}',
            'cachedir': esettings.user_container_cachedir
        }
    else:
        return {
            'dir': None,
            'xml': None,
            'remote_url': metadata.get_uri(),
            'download_dir': esettings.get_xml_wrappers_dir(),
            'outdir': f'{esettings.get_janis_tools_dir()}/{metadata.tool_id}',
            'cachedir': esettings.user_container_cachedir
        }

def get_builtin_tool_path(metadata: StepMetadata) -> Tuple[str, str]:
    import galaxy.tools
    tool_folder = str(galaxy.tools.__file__).rsplit('/', 1)[0]
    xml_files = [f for f in os.listdir(tool_folder) if f.endswith('.xml')]
    for xml in xml_files:
        filepath = f'{tool_folder}/{xml}'
        if metadata.tool_id == etree_utils.get_xml_tool_id(filepath):
            return tool_folder, xml
    raise RuntimeError(f'cant find tool xml for {metadata.tool_id}')


# after parsing
def set_tool_paths(wsettings: WorkflowExeSettings, workflow: Workflow) -> None:
    # write a definition for the workflow
    tools_dir = wsettings.get_janis_tools_dir()
    for step in workflow.list_steps():
        #tool: Tool = step.tool # type: ignore
        #tag = tool.tag_manager.get('tool_name', tool.get_uuid())
        tag = workflow.tag_manager.get_base_tag(step.get_uuid())
        path = f'{tools_dir}/{tag}/{tag}.py'
        step.set_definition_path(path)