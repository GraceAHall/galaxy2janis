

# module entry
import runtime.logging.logging as logging
from typing import Type

from runtime.settings.ExeSettings import ToolExeSettings, WorkflowExeSettings
from runtime.settings.settings import create_tool_settings_for_step

from workflows.entities.workflow.workflow import Workflow
from workflows.entities.step.step import WorkflowStep

from .ValueMigrator import ValueMigrator
from .ValueLinker import (
    ValueLinker,
    CheetahValueLinker, 
    InputDictValueLinker, 
    UnlinkedValueLinker, 
    DefaultValueLinker
)

"""
assigns values for each tool input 
works by using the step input dict in a number of ways: 
- by evaluating the <command> section cheetah in sections, then identifying values
- by directly linking values in the step input dict to tool inputs using gxparams as
  a 'common key'
if a value is still unknown for a given tool input, it
is assigned the default or listed as a WorkflowInput (when it is a file type)
"""

linkers: list[Type[ValueLinker]] = [
    CheetahValueLinker,
    InputDictValueLinker,
    DefaultValueLinker,
    UnlinkedValueLinker
]


def link_tool_input_values(wsettings: WorkflowExeSettings, workflow: Workflow) -> None:
    for step in workflow.list_steps():
        tsettings = create_tool_settings_for_step(wsettings, step.metadata)
        step.inputs.assign_gxparams(step.tool)  # is this needed?
        link_step_values(tsettings, step, workflow)
        assert_all_components_assigned(step)

def link_step_values(esettings: ToolExeSettings, step: WorkflowStep, workflow: Workflow) -> None:
    for linker in linkers:
        l = linker(esettings, step, workflow)
        l.link()
        logging.runtime_data(str(step.tool_values))
    perform_migrations(step, workflow)

def perform_migrations(step: WorkflowStep, workflow: Workflow):
    migrator = ValueMigrator(step, workflow)
    migrator.migrate()

def assert_all_components_assigned(step: WorkflowStep) -> None:
    tool_inputs = step.tool.list_inputs() # type: ignore
    for component in tool_inputs:
        if not step.tool_values.get(component.get_uuid()):
            raise AssertionError(f'tool input "{component.get_name()}" has no assigned step value')