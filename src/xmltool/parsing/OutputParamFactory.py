

from typing import Optional
from runtime.exceptions import AttributeNotSupportedError, ParamNotSupportedError
from galaxy.tool_util.parser.output_objects import ToolOutput as GxOutput

from xmltool.param.InputParamRegister import InputParamRegister
from xmltool.param.Param import Param

from xmltool.parsing.datasets import fetch_datatype
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

    def produce(self, gxout: GxOutput, inputs: InputParamRegister) -> Param:
        self.assert_supported(gxout)
        p_class = FACTORY[gxout.output_type]
        param = p_class(gxout.name)
        param = self.map_common_attrs(gxout, param)
        param = self.map_specific_attrs(gxout, param)
        param.datatypes = fetch_datatype(gxout, inputs)
        param.wildcard_pattern = self.get_wildcard_pattern(gxout)
        return param 
    
    def assert_supported(self, gxout: GxOutput):
        # if gxout.metadata_source and gxout.metadata_source != '':
        #     raise AttributeNotSupportedError('<output> with metadata_source attr')
        if gxout.output_type not in ['data', 'collection']:
            raise ParamNotSupportedError(f'unknown param type: {str(gxout.output_type)}')

    def map_common_attrs(self, gxout: GxOutput, param: OutputParam) -> OutputParam:
        param.label = str(gxout.label).rsplit('}', 1)[-1].strip(': ')
        return param

    def map_specific_attrs(self, gxout: GxOutput, param: OutputParam) -> OutputParam:
        if isinstance(param, CollectionOutputParam):
            if gxout.structure.collection_type != '':
                param.collection_type = str(gxout.structure.collection_type) 
        return param
    
    def get_wildcard_pattern(self, gxout: GxOutput) -> Optional[str]:
        if self.has_from_workdir(gxout):
            return gxout.from_work_dir
        elif self.has_dataset_collector(gxout):
            collector = gxout.dataset_collector_descriptions[0]
            return f'{collector.directory}/{collector.pattern}' # type: ignore
        else:
            return None

    def has_from_workdir(self, gxout: GxOutput) -> bool:
        if gxout.output_type == 'data': # type: ignore
            if hasattr(gxout, 'from_work_dir') and gxout.from_work_dir: # type: ignore
                return True
        return False

    def has_dataset_collector(self, gxout: GxOutput) -> bool:
        if hasattr(gxout, 'dynamic_structure') and gxout.dynamic_structure: # type: ignore
            if hasattr(gxout, 'dataset_collector_descriptions'):
                return True
        return False





