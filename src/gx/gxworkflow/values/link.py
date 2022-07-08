

# module entry
import logs.logging as logging
from typing import Type

from .updates import update_component_knowledge

from entities.workflow import Workflow
from entities.workflow import WorkflowStep

from .linkers.ValueLinker import ValueLinker 
from .linkers.cheetah import CheetahValueLinker 
from .linkers.stepinputs import StepInputsLinker 
from .linkers.default import DefaultValueLinker 
from .linkers.unlinked import UnlinkedValueLinker 

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
    StepInputsLinker,
]

blind_linkers: list[Type[ValueLinker]] = [
    DefaultValueLinker,
    UnlinkedValueLinker
]


def link_step_tool_values(workflow: Workflow) -> None:
    for step in workflow.steps:
        link_step_values(step, workflow)
        assert_all_components_assigned(step)

def link_step_values(step: WorkflowStep, workflow: Workflow) -> None:
    # link values using cheetah cmdstr and input dict
    for linker in knowledge_linkers:
        l = linker(step, workflow)
        l.link()
        logging.runtime_data(str(step.tool_values))
    
    # update component knowledge for components which have been linked so far
    update_component_knowledge(step)
    
    # link remaining values from default, assign unlinked
    for linker in blind_linkers:
        l = linker(step, workflow)
        l.link()
        logging.runtime_data(str(step.tool_values))

def assert_all_components_assigned(step: WorkflowStep) -> None:
    # just for safety
    tool_inputs = step.tool.list_inputs() # type: ignore
    for component in tool_inputs:
        if not step.tool_values.get(component.uuid):
            raise AssertionError(f'tool input "{component.name}" has no assigned step value')