

from __future__ import annotations
from typing import TYPE_CHECKING
from fileio.text.tool.ScriptText import ScriptText

from fileio.text.tool.UnstranslatedText import UntranslatedText

if TYPE_CHECKING:
    from entities.tool import Tool
    from entities.workflow import Workflow
    from entities.workflow import WorkflowStep

import shutil
import paths

from utils import galaxy as galaxy_utils
from gx.wrappers.downloads.cache import DownloadCache
from fileio.text.tool.ToolText import ToolText
from .initialisation import init_folder

from .text.workflow.WorkflowText import WorkflowText

download_cache: DownloadCache = DownloadCache(paths.DOWNLOADED_WRAPPERS_DIR)  # shouldn't do this. should use fetch_wrapper ideally. 


def write_tool(tool: Tool, path: str) -> None:
    text = ToolText(tool)
    page = text.render()
    with open(path, 'w') as fp:
        fp.write(page)

def write_workflow(janis: Workflow) -> None:
    write_tools(janis)
    write_untranslated(janis)
    write_scripts(janis)
    write_wrappers(janis)
    #write_sub_workflows(janis)
    write_main_workflow(janis)
    #write_inputs(janis)
    #write_config(janis)

def write_tools(janis: Workflow) -> None:
    for step in janis.steps:
        tool_id = step.metadata.wrapper.tool_id
        write_tool(step.tool, paths.manager.tool(tool_id))

def write_untranslated(janis: Workflow) -> None:
    for step in janis.steps:
        if step.preprocessing or step.postprocessing:
            tool_id = step.metadata.wrapper.tool_id
            path = paths.manager.untranslated(tool_id)
            text = UntranslatedText(step)
            page = text.render()
            with open(path, 'w') as fp:
                fp.write(page)

def write_scripts(janis: Workflow) -> None:
    for step in janis.steps:
        if step.tool.configfiles:
            tool_id = step.metadata.wrapper.tool_id
            for configfile in step.tool.configfiles:
                path = paths.manager.script(tool_id, configfile.name)
                text = ScriptText(configfile)
                page = text.render()
                with open(path, 'w') as fp:
                    fp.write(page)

def write_wrappers(janis: Workflow) -> None:
    for step in janis.steps:
        src_files = get_wrapper_files_src(step)
        dest = get_wrapper_files_dest(step)
        init_folder(dest)
        for src in src_files:
            shutil.copy2(src, dest)

def get_wrapper_files_src(step: WorkflowStep) -> list[str]:
    repo = step.metadata.wrapper.repo
    tool_id = step.metadata.wrapper.tool_id
    revision = step.metadata.wrapper.revision
    source_dir = download_cache.get(repo, revision)
    assert(source_dir)
    main_xml = galaxy_utils.get_xml_by_id(source_dir, tool_id)
    assert(main_xml)
    macro_xmls = galaxy_utils.get_macros(source_dir)
    xmls = [main_xml] + macro_xmls
    xmls = [f'{source_dir}/{xml}' for xml in xmls]
    return xmls

def get_wrapper_files_dest(step: WorkflowStep) -> str:
    tool_id = step.metadata.wrapper.tool_id
    revision = step.metadata.wrapper.revision
    return paths.manager.wrapper(tool_id, revision)

def write_main_workflow(janis: Workflow) -> None:
    path = paths.manager.workflow()
    text = WorkflowText(janis)
    page = text.render()
    with open(path, 'w') as fp:
        fp.write(page)

def write_inputs(janis: Workflow) -> None:
    raise NotImplementedError()

def write_sub_workflows(janis: Workflow) -> None:
    raise NotImplementedError()

def write_config(janis: Workflow) -> None:
    raise NotImplementedError()







# def write_workflow_tools(workflow: Workflow) -> None:
#     for step in workflow.list_steps():
#         formatter = JanisToolFormatter(step.tool)
#         tool_definition = formatter.to_janis_definition()
#         path = f'{esettings.outdir}/{step.metadata.tool_definition_path}'
#         with open(path, 'w') as fp:
#             fp.write(tool_definition)

# def write_workflow(workflow: Workflow) -> None: 
#     write_workflow_tools(esettings, workflow)
#     write_workflow_definitions(esettings, workflow)


# def write_workflow_definitions(workflow: Workflow) -> None:
#     # inputs dict
#     write_inputs_dict(workflow)

#     # main workflow page
#     text_def = BulkWorkflowTextDefinition(workflow)
#     #text_def = StepwiseWorkflowTextDefinition(esettings, workflow)
#     write_main_page(text_def)
    
#     # individual step pages if necessary
#     if isinstance(text_def, StepwiseWorkflowTextDefinition):
#         write_step_pages(text_def)

# def write_inputs_dict(workflow: Workflow) -> None:
#     FMT = 'yaml'
#     path = esettings.outpaths.inputs(format=FMT)
#     text = format_input_dict(workflow, format=FMT)
#     with open(path, 'w') as fp:
#         fp.write(text)

# def write_main_page(text_def: WorkflowTextDefinition) -> None:
#     path = esettings.outpaths.workflow()
#     with open(path, 'w') as fp:
#         fp.write(text_def.format())
        
# def write_step_pages(text_def: StepwiseWorkflowTextDefinition) -> None:
#     for page in text_def.step_pages:
#         with open(page.path, 'w') as fp:
#             fp.write(page.text)

