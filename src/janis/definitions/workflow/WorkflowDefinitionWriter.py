
from abc import ABC, abstractmethod


class WorkflowDefinitionWriter(ABC):

    @abstractmethod    
    def write(self) -> None:
        ...
    
    @abstractmethod    
    def write_header(self) -> None:
        ...
    
    @abstractmethod
    def write_imports(self) -> None:
        ...

    @abstractmethod
    def write_metadata(self) -> None:
        ...
    
    @abstractmethod
    def write_declaration(self) -> None:
        ...
    
    @abstractmethod
    def write_inputs(self) -> None:
        ...

    @abstractmethod
    def write_steps(self) -> None:
        ...

    @abstractmethod
    def write_outputs(self) -> None:
        ...



