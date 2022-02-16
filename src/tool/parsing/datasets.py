

from abc import ABC
from galaxy.tool_util.parser.output_objects import ToolOutput as GxOutput
from tool.param.InputRegister import InputRegister


# helper classes 
class FetchStrategy(ABC):
    def fetch(self, gxout: GxOutput, inputs: InputRegister) -> list[str]:
        """gets the datatype associated with this galaxy output"""
        ...

class FormatFetchStrategy(FetchStrategy):
    def fetch(self, gxout: GxOutput, inputs: InputRegister) -> list[str]:
        return str(gxout.format).split(',')

class DefaultFormatFetchStrategy(FetchStrategy):
    def fetch(self, gxout: GxOutput, inputs: InputRegister) -> list[str]:
        return str(gxout.default_format).split(',')

class FormatSourceFetchStrategy(FetchStrategy):
    def fetch(self, gxout: GxOutput, inputs: InputRegister) -> list[str]:
        param = inputs.get(gxout.format_source, strategy='lca')
        if param:
            return param.datatypes
        return ['data']

class CollectorFetchStrategy(FetchStrategy):
    def fetch(self, gxout: GxOutput, inputs: InputRegister) -> list[str]:
        coll = gxout.dataset_collector_descriptions[0]
        if coll.default_ext:
            return str(coll.default_ext).split(',')
        return ['data']

class FallbackFetchStrategy(FetchStrategy):
    def fetch(self, gxout: GxOutput, inputs: InputRegister) -> list[str]:
        return ['data']


def fetch_datatype(gxout: GxOutput, inputs: InputRegister) -> list[str]:
    strategy: FetchStrategy = select_fetcher(gxout)
    return strategy.fetch(gxout, inputs)

def select_fetcher(gxout: GxOutput) -> FetchStrategy:
    if has_format(gxout):
        return FormatFetchStrategy()
    elif has_default_format(gxout):
        return DefaultFormatFetchStrategy()
    elif has_format_source(gxout):
        return FormatSourceFetchStrategy()
    elif has_dataset_collector(gxout):
        return CollectorFetchStrategy()
    else:
        return FallbackFetchStrategy()

def has_format(gxout: GxOutput) -> bool:
    if hasattr(gxout, 'format'):
        if gxout.format and gxout.format != 'data':
            return True
    return False

def has_default_format(gxout: GxOutput) -> bool:
    if hasattr(gxout, 'default_format'): 
        if gxout.default_format and gxout.default_format != 'data':
            return True
    return False

def has_format_source(gxout: GxOutput) -> bool:
    if hasattr(gxout, 'format_source'):
        if gxout.format_source:
            return True
    return False
    
def has_dataset_collector(gxout: GxOutput) -> bool:
    return False


