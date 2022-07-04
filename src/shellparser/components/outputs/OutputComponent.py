



from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional

from uuid import uuid4
from gx.xmltool.param.Param import Param


class OutputComponent(ABC):
    def __init__(self):
        self.uuid: str = str(uuid4())
        self.gxparam: Optional[Param] = None
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



