


from abc import ABC, abstractmethod


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
    def tool(self, tool_id: str) -> str:
        """specifies where the provided tool should be written"""
        ...
    
    @abstractmethod
    def wrapper(self, tool_id: str, revision: str) -> str:
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
    
    def tool(self, tool_id: str) -> str:
        return f'{self._project_dir}/{tool_id}.py'

    def wrapper(self, tool_id: str, revision: str) -> str:
        raise NotImplementedError()


# workflow mode 
class WorkflowModePathManager(PathManager):
    """specifies folder and file paths for output files"""

    _subfolders: list[str] = [
        'logs',
        'wrappers',
        'tools',
        'subworkflows',
        'scripts',
    ]
    
    def workflow(self) -> str:
        return f'{self._project_dir}/workflow.py'
    
    def inputs(self, format: str='yaml') -> str:
        return f'{self._project_dir}/inputs.{format}'
    
    def config(self, format: str='yaml') -> str:
        return f'{self._project_dir}/config.{format}'
    
    def tool(self, tool_id: str) -> str:
        return f'{self._project_dir}/tools/{tool_id}.py'
    
    def subworkflow(self, tool_id: str) -> str:
        return f'{self._project_dir}/subworkflows/{tool_id}.py'
    
    def script(self, tool_id: str) -> str: # TODO script name?
        return f'{self._project_dir}/scripts/{tool_id}.py'

    def wrapper(self, tool_id: str, revision: str) -> str:
        return f'{self._project_dir}/wrappers/{tool_id}-{revision}'

