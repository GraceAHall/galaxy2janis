


from abc import ABC, abstractmethod
from dataclasses import dataclass

from entities.workflow.workflow import Workflow
from entities.workflow.step.step import WorkflowStep


@dataclass
class PathManager(ABC):
    """specifies folder and file paths for output files"""
    _outdir: str
    
    @abstractmethod
    def workflow(self) -> str:
        """specifies where the workflow text should be written"""
        ...
    
    @abstractmethod
    def workflow_log(self) -> str:
        """specifies where the workflow logfile should be written"""
        ...
    
    @abstractmethod
    def inputs(self, format: str='yaml') -> str:
        """locations of the inputs.yaml file (or inputs.json)"""
        ...
    
    @abstractmethod
    def step(self, step: WorkflowStep, workflow: Workflow) -> str:
        """specifies where the provided step should be written"""
        ...
    
    @abstractmethod
    def tool(self, step: WorkflowStep, workflow: Workflow) -> str:
        """specifies where the provided tool should be written"""
        ...
    
    @abstractmethod
    def tool_log(self, step: WorkflowStep, workflow: Workflow) -> str:
        """specifies where the tool logfile should be written"""
        ...
    
    @abstractmethod
    def wrapper(self, step: WorkflowStep, workflow: Workflow) -> str:
        """specifies where the macro resolved galaxy wrapper.xml should be written"""
        ...


class UnifiedPathManager(PathManager):
    folder_structure: list[str] = [
        'steps',
        'tools',
        'wrappers',
        'logs'
    ]
    
    def workflow(self) -> str:
        return f'{self._outdir}/workflow.py'
    
    def workflow_log(self) -> str:
        return f'{self._outdir}/workflow.log'
    
    def inputs(self, format: str='yaml') -> str:
        return f'{self._outdir}/inputs.{format}'
    
    def step(self, step: WorkflowStep, workflow: Workflow) -> str:
        raise NotImplementedError()  # no .py file for a step using this format
    
    def tool(self, step: WorkflowStep, workflow: Workflow) -> str:
        tool_id = step.metadata.wrapper.tool_id
        return f'{self._outdir}/tools/{tool_id}.py'

    def tool_log(self, step: WorkflowStep, workflow: Workflow) -> str:
        step_tag = workflow.tag_manager.get(step.uuid)
        return f'{self._outdir}/logs/{step_tag}_tool.log'   # can't be tool_id: not unique
    
    def wrapper(self, step: WorkflowStep, workflow: Workflow) -> str:
        tool_id = step.metadata.wrapper.tool_id
        revision = step.metadata.wrapper.revision  
        return f'{self._outdir}/wrappers/{tool_id}-{revision}'



class StepwisePathManager(PathManager):
    folder_structure: list[str] = [
        'steps'
    ]
    
    def workflow(self) -> str:
        return f'{self._outdir}/workflow.py'
    
    def workflow_log(self) -> str:
        return f'{self._outdir}/workflow.log'
    
    def inputs(self, format: str='yaml') -> str:
        return f'{self._outdir}/inputs.{format}'
    
    def step(self, step: WorkflowStep, workflow: Workflow) -> str:
        step_tag = workflow.tag_manager.get(step.uuid)
        return f'{self._outdir}/{step_tag}/{step_tag}_step.py'
    
    def tool(self, step: WorkflowStep, workflow: Workflow) -> str:
        step_tag = workflow.tag_manager.get(step.uuid)
        tool_id = step.metadata.wrapper.tool_id
        return f'{self._outdir}/{step_tag}/{tool_id}.py'
    
    def tool_log(self, step: WorkflowStep, workflow: Workflow) -> str:
        step_tag = workflow.tag_manager.get(step.uuid)
        return f'{self._outdir}/{step_tag}/tool.log'
    
    def wrapper(self, step: WorkflowStep, workflow: Workflow) -> str:
        step_tag = workflow.tag_manager.get(step.uuid)
        tool_id = step.metadata.wrapper.tool_id  
        revision = step.metadata.wrapper.revision  
        return f'{self._outdir}/{step_tag}/{tool_id}-{revision}'
     



