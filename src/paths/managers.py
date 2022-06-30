

import settings

from abc import ABC, abstractmethod
from typing import Optional

from entities.workflow import WorkflowStep



class PathManager(ABC):
    """specifies folder and file paths for output files"""
    
    @abstractmethod
    def outdir(self) -> str:
        """specifies parent output directory"""
        ...
    
    @abstractmethod
    def workflow(self) -> str:
        """specifies where the workflow text should be written"""
        ...
    
    @abstractmethod
    def inputs(self, format: str='yaml') -> str:
        """locations of the inputs.yaml file (or inputs.json)"""
        ...
    
    @abstractmethod
    def step(self, step: Optional[WorkflowStep]=None) -> str:
        """specifies where the provided step should be written"""
        ...
    
    @abstractmethod
    def tool(self, step: Optional[WorkflowStep]=None) -> str:
        """specifies where the provided tool should be written"""
        ...
    
    @abstractmethod
    def wrapper(self, step: Optional[WorkflowStep]=None) -> str:
        """specifies where the macro resolved galaxy wrapper.xml should be written"""
        ...

# tool mode 
class ToolModePathManager(PathManager):
    """specifies folder and file paths for output files"""
    
    folder_structure: list[str] = []

    def outdir(self) -> str:
        return settings.general.outdir

    def workflow(self) -> str:
        raise NotImplementedError()  # not needed for tool mode
    
    def inputs(self, format: str='yaml') -> str:
        raise NotImplementedError()  # not needed for tool mode
    
    def step(self, step: Optional[WorkflowStep]=None) -> str:
        raise NotImplementedError()  # not needed for tool mode

    def tool(self, step: Optional[WorkflowStep]=None) -> str:
        return f'{settings.general.outdir}/{settings.tool.tool_id}/{settings.tool.tool_id}.py'

    def wrapper(self, step: Optional[WorkflowStep]=None) -> str:
        raise NotImplementedError()


# workflow mode 
class WorkflowModePathManager(PathManager):
    """specifies folder and file paths for output files"""

    folder_structure: list[str] = [
        'tools',
        'wrappers',
        'logs'
    ]
    
    def outdir(self) -> str:
        return settings.general.outdir

    def workflow(self) -> str:
        return f'{settings.general.outdir}/workflow.py'
    
    def inputs(self, format: str='yaml') -> str:
        return f'{settings.general.outdir}/inputs.{format}'
    
    def step(self, step: Optional[WorkflowStep]=None) -> str:
        raise NotImplementedError()  # no .py file for a step using this format
    
    def tool(self, step: Optional[WorkflowStep]=None) -> str:
        assert(step)
        tool_id = step.metadata.wrapper.tool_id
        return f'{settings.general.outdir}/tools/{tool_id}.py'

    def wrapper(self, step: Optional[WorkflowStep]=None) -> str:
        assert(step)
        tool_id = step.metadata.wrapper.tool_id
        revision = step.metadata.wrapper.revision  
        return f'{settings.general.outdir}/wrappers/{tool_id}-{revision}'


# # workflow mode 
# class StepwiseFormatPathManager:
#     folder_structure: list[str] = [
#         'steps'
#     ]
    
#     def workflow(self) -> str:
#         return f'{settings.general.outdir}/workflow.py'
    
#     def inputs(self, format: str='yaml') -> str:
#         return f'{settings.general.outdir}/inputs.{format}'
    
#     def step(self, step: Optional[WorkflowStep]=None) -> str:
#         step_tag = tags.workflow.get(step.uuid)
#         return f'{settings.general.outdir}/{step_tag}/{step_tag}_step.py'
    
#     def tool(self, step: Optional[WorkflowStep]=None) -> str:
#         step_tag = tags.workflow.get(step.uuid)
#         tool_id = step.metadata.wrapper.tool_id
#         return f'{settings.general.outdir}/{step_tag}/{tool_id}.py'
    
#     def wrapper(self, step: Optional[WorkflowStep]=None) -> str:
#         step_tag = tags.workflow.get(step.uuid)
#         tool_id = step.metadata.wrapper.tool_id  
#         revision = step.metadata.wrapper.revision  
#         return f'{settings.general.outdir}/{step_tag}/{tool_id}-{revision}'
     


