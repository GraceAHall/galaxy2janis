





from galaxy.tools.parameters.basic import ToolParameter as GalaxyParam
from tool.param.Param import Param
from tool.param.InputParam import (
    TextParam,
    IntegerParam,
    FloatParam,
    BoolParam,
    SelectParam,
    DataParam,
    DataCollectionParam
)



"""
get the param class
instantiate with a name
map common
map class specific
"""


param_map = {
    'text': TextParam,
    'integer': IntegerParam,
    'float': FloatParam,
    'boolean': BoolParam,
    'select': SelectParam,
    'data': DataParam,
    'data_collection': DataCollectionParam
}


class ParamFactory:
    def create(self, gxparam: GalaxyParam) -> Param:
        paramclass = param_map[str(gxparam.type)]
        param = paramclass(str(gxparam.name))




def map_param(gxparam: GalaxyParam) -> Param:
    match gxparam.type: # type: ignore
        case 'text':
            return init_text_param(gxparam)
        case 'integer':
            return init_int_param(gxparam)
        case 'float':
            return init_float_param(gxparam)
        case 'boolean':
            return init_bool_param(gxparam)
        case 'select':
            return init_select_param(gxparam)
        case 'data':
            return init_data_param(gxparam)
        case 'data_collection':
            return init_data_collection_param(gxparam)


def init_text_param(gxparam: GalaxyParam) -> TextParam:
    raise NotImplementedError

def init_int_param(gxparam: GalaxyParam) -> IntegerParam:
    raise NotImplementedError

def init_float_param(gxparam: GalaxyParam) -> FloatParam:
    raise NotImplementedError

def init_bool_param(gxparam: GalaxyParam) -> BoolParam:
    raise NotImplementedError

def init_select_param(gxparam: GalaxyParam) -> SelectParam:
    raise NotImplementedError

def init_data_param(gxparam: GalaxyParam) -> DataParam:
    raise NotImplementedError

def init_data_collection_param(gxparam: GalaxyParam) -> DataCollectionParam:
    raise NotImplementedError


def map_common_fields(gxparam: GalaxyParam, param: Param) -> Param:
    param.label = str(gxparam.label)
    param.helptext = str(gxparam.help)
    param.optional = bool(gxparam.optional)
    param.argument = gxparam.argument
    return param
