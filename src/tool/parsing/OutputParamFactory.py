

from logger.errors import AttributeNotSupportedError, ParamNotSupportedError

from tool.parsing.GalaxyOutput import GalaxyOutput
from tool.parsing.DatatypeFetcher import DatatypeFetcher
from tool.parsing.WildcardFetcher import WildcardFetcher
from tool.param.Param import Param

from tool.param.OutputParam import (
    OutputParam,
    DataOutputParam,
    CollectionOutputParam,
)

FACTORY = {
    'data': DataOutputParam,
    'collection': CollectionOutputParam
}

class OutputParamFactory:
    def produce(self, gxout: GalaxyOutput) -> Param:
        self.assert_supported(gxout)
        p_class = FACTORY[gxout.output_type]
        param = p_class(gxout.name)
        param = self.map_common_attrs(gxout, param)
        param = self.map_specific_attrs(gxout, param)
        param.datatypes = DatatypeFetcher().get(gxout)
        param.files_wildcard = WildcardFetcher().get(gxout)
        return param 
    
    def map_common_attrs(self, gxout: GalaxyOutput, param: OutputParam) -> OutputParam:
        param.label = str(gxout.label).rsplit('}', 1)[-1].strip(': ')
        return param

    def map_specific_attrs(self, gxout: GalaxyOutput, param: OutputParam) -> OutputParam:
        match param:
            case CollectionOutputParam():
                if gxout.structure.collection_type != '':
                    param.collection_type = str(gxout.structure.collection_type) 
            case _:
                pass
        return param
        
    def assert_supported(self, gxout: GalaxyOutput):
        if gxout.format_source:
            raise AttributeNotSupportedError('<output> with format_source attr')
        if gxout.metadata_source and gxout.metadata_source != '':
            raise AttributeNotSupportedError('<output> with metadata_source attr')
        if gxout.output_type not in ['data', 'collection']:
            raise ParamNotSupportedError(f'unknown param type: {str(gxout.output_type)}')
    


