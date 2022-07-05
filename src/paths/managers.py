


from abc import ABC, abstractmethod
from typing import Optional

from entities.workflow.step.metadata import StepMetadata
import settings


class PathManager(ABC):
    
    _subfolders: list[str]

    """specifies folder and file paths for output files"""
    def __init__(self, project_dir: str):
        self._project_dir = project_dir

    def project_dir(self) -> str:
        return self._project_dir
    
    def subfolders(self) -> list[str]:
        return self._subfolders

    def janis_log(self) -> str:
        return f'{self._project_dir}/logs/janis.log'
    
    def message_log(self) -> str:
        return f'{self._project_dir}/logs/messages.log'
    
    @abstractmethod
    def workflow(self) -> str:
        """specifies where the workflow text should be written"""
        ...
    
    @abstractmethod
    def inputs(self, format: str='yaml') -> str:
        """locations of the inputs.yaml file (or inputs.json)"""
        ...
    
    @abstractmethod
    def step(self, metadata: Optional[StepMetadata]=None) -> str:
        """specifies where the provided step should be written"""
        ...
    
    @abstractmethod
    def tool(self, metadata: Optional[StepMetadata]=None) -> str:
        """specifies where the provided tool should be written"""
        ...
    
    @abstractmethod
    def wrapper(self, metadata: Optional[StepMetadata]=None) -> str:
        """specifies where the macro resolved galaxy wrapper.xml should be written"""
        ...

# tool mode 
class ToolModePathManager(PathManager):
    """specifies folder and file paths for output files"""
    
    _subfolders: list[str] = [
        'logs'
    ]

    def workflow(self) -> str:
        raise NotImplementedError()  # not needed for tool mode
    
    def inputs(self, format: str='yaml') -> str:
        raise NotImplementedError()  # not needed for tool mode
    
    def step(self, metadata: Optional[StepMetadata]=None) -> str:
        raise NotImplementedError()  # not needed for tool mode

    def tool(self, metadata: Optional[StepMetadata]=None) -> str:
        return f'{self._project_dir}/{settings.tool.tool_id}.py'

    def wrapper(self, metadata: Optional[StepMetadata]=None) -> str:
        raise NotImplementedError()


# workflow mode 
class WorkflowModePathManager(PathManager):
    """specifies folder and file paths for output files"""

    _subfolders: list[str] = [
        'logs',
        'tools',
        'wrappers',
    ]
    
    def workflow(self) -> str:
        return f'{self._project_dir}/workflow.py'
    
    def inputs(self, format: str='yaml') -> str:
        return f'{self._project_dir}/inputs.{format}'
    
    def step(self, metadata: Optional[StepMetadata]=None) -> str:
        raise NotImplementedError()  # no .py file for a step using this format
    
    def tool(self, metadata: Optional[StepMetadata]=None) -> str:
        assert(metadata)
        tool_id = metadata.wrapper.tool_id
        return f'{self._project_dir}/tools/{tool_id}.py'

    def wrapper(self, metadata: Optional[StepMetadata]=None) -> str:
        assert(metadata)
        tool_id = metadata.wrapper.tool_id
        revision = metadata.wrapper.revision  
        return f'{self._project_dir}/wrappers/{tool_id}-{revision}'


# # workflow mode 
# class StepwiseFormatPathManager:
#     _subfolders: list[str] = [
#         'steps'
#     ]
    
#     def workflow(self) -> str:
#         return f'{self.outdir}/workflow.py'
    
#     def inputs(self, format: str='yaml') -> str:
#         return f'{self.outdir}/inputs.{format}'
    
#     def step(self, metadata: Optional[StepMetadata]=None) -> str:
#         step_tag = tags.workflow.get(step.uuid)
#         return f'{self.outdir}/{step_tag}/{step_tag}_step.py'
    
#     def tool(self, metadata: Optional[StepMetadata]=None) -> str:
#         step_tag = tags.workflow.get(step.uuid)
#         tool_id = step.metadata.wrapper.tool_id
#         return f'{self.outdir}/{step_tag}/{tool_id}.py'
    
#     def wrapper(self, metadata: Optional[StepMetadata]=None) -> str:
#         step_tag = tags.workflow.get(step.uuid)
#         tool_id = step.metadata.wrapper.tool_id  
#         revision = step.metadata.wrapper.revision  
#         return f'{self.outdir}/{step_tag}/{tool_id}-{revision}'
     


