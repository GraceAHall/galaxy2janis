

from runtime.exceptions import AttributeNotSupportedError, ParamNotSupportedError
from galaxy.tool_util.parser.output_objects import ToolOutput as GxOutput

from xmltool.param.InputRegister import InputRegister
from xmltool.param.Param import Param

from xmltool.parsing.datasets import fetch_datatype
from xmltool.parsing.selectors import fetch_selector
from xmltool.param.OutputParam import (
    OutputParam,
    DataOutputParam,
    CollectionOutputParam,
)

FACTORY = {
    'data': DataOutputParam,
    'collection': CollectionOutputParam
}

class OutputParamFactory:

    def produce(self, gxout: GxOutput, inputs: InputRegister) -> Param:
        self.assert_supported(gxout)
        p_class = FACTORY[gxout.output_type]
        param = p_class(gxout.name)
        param = self.map_common_attrs(gxout, param)
        param = self.map_specific_attrs(gxout, param)
        param.datatypes = fetch_datatype(gxout, inputs)
        param.selector = fetch_selector(gxout)
        return param 
    
    def map_common_attrs(self, gxout: GxOutput, param: OutputParam) -> OutputParam:
        param.label = str(gxout.label).rsplit('}', 1)[-1].strip(': ')
        return param

    def map_specific_attrs(self, gxout: GxOutput, param: OutputParam) -> OutputParam:
        match param:
            case CollectionOutputParam():
                if gxout.structure.collection_type != '':
                    param.collection_type = str(gxout.structure.collection_type) 
            case _:
                pass
        return param

    def assert_supported(self, gxout: GxOutput):
        # if gxout.metadata_source and gxout.metadata_source != '':
        #     raise AttributeNotSupportedError('<output> with metadata_source attr')
        if gxout.output_type not in ['data', 'collection']:
            raise ParamNotSupportedError(f'unknown param type: {str(gxout.output_type)}')



