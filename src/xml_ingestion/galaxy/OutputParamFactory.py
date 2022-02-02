


from typing import Optional, Protocol

from logger.errors import ParamNotSupportedError
from tool.param.Param import Param
from tool.param.OutputParam import (
    OutputParam,
    DataOutputParam,
    CollectionOutputParam,
)


class GalaxyOutput(Protocol):
    """
    strucutral pattern matching used in this file.
    galaxy objects aren't always typed or well written.
    better to just define what properties an object needs to 'pass' as
    a GalaxyOutput
    """
    name: str
    label: str
    output_type: str
    format_source: Optional[str] = None


class OutputParamFactory:
    def produce(self, gxout: GalaxyOutput) -> Param:
        match gxout.type: # type: ignore
            case 'data':
                param = self.init_data_param(gxout)
            case 'integer':
                param = self.init_collection_param(gxout)
            case _:
                raise ParamNotSupportedError(f'unknown param type: {str(gxout.type)}')
        
        param = self.map_common_fields(gxout, param) #type: ignore
        return param 
        
    def map_common_fields(self, gxout: GalaxyOutput, param: OutputParam) -> OutputParam:
        param.label = str(gxout.label)
        param.format_source = gxout.format_source
        return param

    def init_data_param(self, gxout: GalaxyOutput) -> DataOutputParam:
        param = DataOutputParam(str(gxout.name))
        param.format = gxout.format
        param.from_work_dir = gxout.from_work_dir
        return param

    def init_collection_param(self, gxout: GalaxyOutput) -> CollectionOutputParam:
        param = CollectionOutputParam(str(gxout.name))
        return param


