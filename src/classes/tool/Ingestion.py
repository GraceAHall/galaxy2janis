


from typing import Protocol
from galaxy.tools import Tool as GalaxyTool

from classes.tool.InputParam import GenericInputParam
from classes.tool.OutputParam import GenericOutputParam
from classes.tool.Test import Test
from classes.tool.Requirement import Requirement
from classes.tool.Metadata import Metadata


class IngestStrategy(Protocol):
    def get_metadata(self, repr: GalaxyTool) -> Metadata:
        """returns a formatted Metadata using the representation"""
        ...
    
    def get_requirements(self, repr: GalaxyTool) -> list[Requirement]:
        """returns a formatted list of Requirements using the representation"""
        ...
    
    def get_params(self, repr: GalaxyTool) -> list[GenericInputParam]:
        """returns a formatted list of params using the representation"""
        ...
    
    def get_outputs(self, repr: GalaxyTool) -> list[GenericOutputParam]:
        """returns a formatted list of outputs using the representation"""
        ...
    
    def get_tests(self, repr: GalaxyTool) -> list[Test]:
        """returns a formatted list of tests using the representation"""
        ...


class GalaxyIngestStrategy:
    def get_metadata(self, repr: GalaxyTool) -> Metadata:
        """returns a formatted Metadata using the representation"""
        raise NotImplementedError
    
    def get_requirements(self, repr: GalaxyTool) -> list[Requirement]:
        """returns a formatted list of Requirements using the representation"""
        raise NotImplementedError
    
    def get_params(self, repr: GalaxyTool) -> list[GenericInputParam]:
        """returns a formatted list of params using the representation"""
        raise NotImplementedError
    
    def get_outputs(self, repr: GalaxyTool) -> list[GenericOutputParam]:
        """returns a formatted list of outputs using the representation"""
        raise NotImplementedError
    
    def get_tests(self, repr: GalaxyTool) -> list[Test]:
        """returns a formatted list of tests using the representation"""
        raise NotImplementedError


class LocalIngestStrategy:
    def get_metadata(self, repr: GalaxyTool) -> Metadata:
        """returns a formatted Metadata using the representation"""
        raise NotImplementedError
    
    def get_requirements(self, repr: GalaxyTool) -> list[Requirement]:
        """returns a formatted list of Requirements using the representation"""
        raise NotImplementedError
    
    def get_params(self, repr: GalaxyTool) -> list[GenericInputParam]:
        """returns a formatted list of params using the representation"""
        raise NotImplementedError
    
    def get_outputs(self, repr: GalaxyTool) -> list[GenericOutputParam]:
        """returns a formatted list of outputs using the representation"""
        raise NotImplementedError
    
    def get_tests(self, repr: GalaxyTool) -> list[Test]:
        """returns a formatted list of tests using the representation"""
        raise NotImplementedError
