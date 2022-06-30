

# module entry
import logs.logging as logging
from typing import Type

import settings
from workflows.analysis.tool_values.component_updates import update_component_knowledge

from entities.tool import Tool
from entities.workflow import Workflow
from entities.workflow import WorkflowStep

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

knowledge_linkers: list[Type[ValueLinker]] = [
    CheetahValueLinker,
    InputDictValueLinker,
]

blind_linkers: list[Type[ValueLinker]] = [
    DefaultValueLinker,
    UnlinkedValueLinker
]


def link_workflow_tool_values(workflow: Workflow) -> Workflow:
    for step in workflow.list_steps():
        settings.tool = create_tool_settings_for_step(settings.workflow, step.metadata)
        assign_gxparams(step.tool, step.inputs)  # is this needed?
        link_step_values(settings.tool, step, workflow)
        assert_all_components_assigned(step)
    return workflow

def assign_gxparams(self, tool: Tool) -> None:
    for step_input in self.register:
        step_input.gxparam = tool.get_gxparam(step_input.gxvarname)
 

def link_step_values(step: WorkflowStep, workflow: Workflow) -> None:
    # link values using cheetah cmdstr and input dict
    for linker in knowledge_linkers:
        l = linker(esettings, step, workflow)
        l.link()
        logging.runtime_data(str(step.tool_values))
    
    # update component knowledge for components which have been linked so far
    update_component_knowledge(step)
    
    # link remaining values from default, assign unlinked
    for linker in blind_linkers:
        l = linker(esettings, step, workflow)
        l.link()
        logging.runtime_data(str(step.tool_values))
    
    # migrate value types if necessary
    perform_migrations(step, workflow)

def perform_migrations(step: WorkflowStep, workflow: Workflow):
    migrator = ValueMigrator(step, workflow)
    migrator.migrate()

def assert_all_components_assigned(step: WorkflowStep) -> None:
    tool_inputs = step.tool.list_inputs() # type: ignore
    for component in tool_inputs:
        if not step.tool_values.get(component.uuid):
            raise AssertionError(f'tool input "{component.name}" has no assigned step value')