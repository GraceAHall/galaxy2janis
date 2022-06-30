

import settings

from typing import Any

from entities.workflow import StepMetadata

from .inputs import parse_step_inputs
from .outputs import parse_step_outputs
from .metadata import parse_step_metadata

from entities.workflow import Workflow
from entities.workflow import WorkflowStep
from tool_mode import tool_mode




# MODULE ENTRY
def parse_tool_step(step: dict[str, Any]) -> WorkflowStep:
    return WorkflowStep(
        metadata=parse_step_metadata(step),
    )



# def parse_tool_step(step: dict[str, Any]) -> WorkflowStep:
#     metadata = parse_step_metadata(step)
#     settings.tool = create_tool_settings_for_step(settings.workflow, metadata)
#     tool = tool_mode(settings.tool)

#     return WorkflowStep(
#         metadata=metadata,
#         inputs=parse_step_inputs(step, workflow, settings.tool),
#         outputs=parse_step_outputs(step)
#     )


# def create_tool_settings_for_step(metadata: StepMetadata, settings.workflow: WorkflowExeSettings) -> dict[str, Any]:
#     if metadata.wrapper.inbuilt:
#         tool_dir, xml_filename = get_builtin_tool_path(metadata)
#         return {
#             'dir': tool_dir,
#             'xml': xml_filename,
#             'remote_url': None,
#             'download_dir': None,
#             'outdir': f'{settings.workflow.get_janis_tools_dir()}/{metadata.wrapper.tool_id}',
#             'cachedir': settings.workflow.container_cachedir,
#             'dev_no_test_cmdstrs': settings.workflow.dev_no_test_cmdstrs
#         }
#     else:
#         return {
#             'dir': None,
#             'xml': None,
#             'remote_url': metadata.wrapper.url,
#             'download_dir': settings.workflow.outpaths.wrapper(),
#             'outdir': f'{settings.workflow.get_janis_tools_dir()}/{metadata.wrapper.tool_id}',
#             'cachedir': settings.workflow.container_cachedir,
#             'dev_no_test_cmdstrs': settings.workflow.dev_no_test_cmdstrs
#         }
