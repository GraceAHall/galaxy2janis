

from __future__ import annotations
from abc import ABC
from typing import Any, Optional, Protocol
from tool.param.Param import Param


# defines what a CommandComponent should look like
class CommandComponent(Protocol):
    gxvar: Optional[Param]
    presence_array: list[bool]
    
    def update(self, incoming: Any):
        ...

    def update_presence_array(self, cmdstr_index: int, fill_false: bool=False):
        ...
    
    def get_default_value(self) -> Any:
        ...

    def get_datatype(self) -> list[str]:
        ...
    
    def is_optional(self) -> bool:
        ...

    def is_array(self) -> bool:
        ...


# this mainly exists because each CommandComponent has the same 
# update_presence_array method. 
class BaseCommandComponent(ABC):
    gxvar: Optional[Param]
    presence_array: list[bool]
    
    def update(self, incoming: Any):
        """
        updates this component with information from another similar component. 
        also sets the component as being present in the cmdstr being parsed.
        example: 
        str1: abricate $input.fastq --db card > out.txt
        str2: abricate $input.fastq --db resfinder > out.txt
        the --db option should be updated so we know its possible values
        are (at least) card, resfinder
        """
        ...

    def update_presence_array(self, cmdstr_index: int, fill_false: bool=False):
        """
        sets the presence of the component in the current cmdstr being parsed.
        This is quite tricky logic, dont change
        """
        # ensure presence array is filled in to current cmdstr
        while len(self.presence_array) < cmdstr_index:
            self.presence_array.append(False)
        
        # now that component is up to date
        if len(self.presence_array) < cmdstr_index + 1:
            if fill_false:
                self.presence_array.append(False)
            else:
                self.presence_array.append(True)
    
    def get_default_value(self) -> Any:
        """
        gets the default value of the component.
        uses the components observed values (positionals / options) and
        galaxy param information if available.
        """
        ...

    def get_datatype(self) -> list[str]:
        """returns the components datatype"""
        ...
    
    def is_optional(self) -> bool:
        """
        returns whether the component is optional or not.
        uses galaxy param information if available, otherwise uses the presence array. flags are always optional
        """
        ...

    def is_array(self) -> bool:
        """
        returns whether the component is an array or not
        uses galaxy param information if available.
        flags components are never arrays.
        """
        ...


