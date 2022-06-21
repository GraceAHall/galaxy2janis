

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Optional, Protocol
from datatypes import JanisDatatype
from xmltool.param.Param import Param
from datatypes import format_janis_str
from uuid import uuid4


# defines what a CommandComponent should look like
class CommandComponent(Protocol):
    uuid: str
    gxparam: Optional[Param]
    cmd_pos: int
    presence_array: list[bool]
    janis_datatypes: list[JanisDatatype]
    forced_optionality: Optional[bool]

    @property
    def name(self) -> str:
        ...

    @property
    def default_value(self) -> Any:
        ...

    @property
    def optional(self) -> bool:
        ...

    @property
    def array(self) -> bool:
        ...
    
    @property
    def docstring(self) -> Optional[str]:
        ...

    def set_janis_datatypes(self, datatypes: list[JanisDatatype]) -> None:
        ...

    def get_janis_datatype_str(self) -> str:
        ...
    
    def update(self, incoming: Any) -> None:
        ...

    def update_presence_array(self, cmdstr_index: int, fill_false: bool=False) -> None:
        ...



# this mainly exists because each CommandComponent has the same 
# update_presence_array() and method. 
class BaseCommandComponent(ABC):
    def __init__(self):
        self.uuid: str = str(uuid4())
        self.gxparam: Optional[Param] = None
        self.cmd_pos: int = -1
        self.presence_array: list[bool] = []
        self.janis_datatypes: list[JanisDatatype] = []
        self.forced_optionality: Optional[bool] = None
 
    @property
    @abstractmethod
    def name(self) -> str:
        """
        returns a name for this component. created depending on what
        information is available to the component
        """
        ...

    @property
    @abstractmethod
    def default_value(self) -> Any:
        """
        gets the default value of the component.
        uses the components observed values (positionals / options) and
        galaxy param information if available.
        """
        ...


    @property
    @abstractmethod
    def optional(self) -> bool:
        """
        returns whether the component is optional or not.
        uses galaxy param information if available, otherwise uses the presence array. flags are always optional
        """
        ...

    @property
    @abstractmethod
    def array(self) -> bool:
        """
        returns whether the component is an array or not
        uses galaxy param information if available.
        flags components are never arrays.
        """
        ...

    @property
    @abstractmethod
    def docstring(self) -> Optional[str]:
        """
        gets helptext for the component. uses galaxy param if available,
        otherwise usually just presents the witnessed values as examples. 
        """
        ...

    def set_janis_datatypes(self, datatypes: list[JanisDatatype]) -> None:
        self.janis_datatypes = datatypes

    def get_janis_datatype_str(self) -> str:
        """gets the janis datatypes then formats into a string for writing definitions"""
        return format_janis_str(
            datatypes=self.janis_datatypes,
            is_optional=self.optional,
            is_array=self.array
        )

    @abstractmethod
    def update(self, incoming: Any) -> None:
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

    def update_presence_array(self, cmdstr_index: int, fill_false: bool=False) -> None:
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


