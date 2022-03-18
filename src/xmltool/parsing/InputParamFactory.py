


from galaxy.tools.parameters.basic import ToolParameter as GalaxyParam

from runtime.exceptions import ParamNotSupportedError
from xmltool.param.Param import Param
from xmltool.param.InputParam import (
    InputParam,
    SelectOption,
    TextParam,
    IntegerParam,
    FloatParam,
    BoolParam,
    SelectParam,
    DataParam,
    DataCollectionParam
)


class InputParamFactory:
    def produce(self, gxparam: GalaxyParam) -> Param:
        match gxparam.type: # type: ignore
            case 'text':
                param = self.init_text_param(gxparam)
            case 'integer':
                param = self.init_int_param(gxparam)
            case 'float':
                param = self.init_float_param(gxparam)
            case 'boolean':
                param = self.init_bool_param(gxparam)
            case 'select':
                param = self.init_select_param(gxparam)
            case 'data':
                param = self.init_data_param(gxparam)
            case 'data_collection':
                param = self.init_data_collection_param(gxparam)
            case _:
                raise ParamNotSupportedError(f'unknown param type: {str(gxparam.type)}')
        
        param = self.map_common_fields(gxparam, param)
        return param 
        
    def map_common_fields(self, gxparam: GalaxyParam, param: InputParam) -> InputParam:
        param.label = str(gxparam.label)
        param.helptext = str(gxparam.help)
        param.optional = bool(gxparam.optional)
        param.argument = gxparam.argument
        return param

    def init_text_param(self, gxparam: GalaxyParam) -> TextParam:
        param = TextParam(str(gxparam.flat_name))
        param.value = gxparam.value
        return param

    def init_int_param(self, gxparam: GalaxyParam) -> IntegerParam:
        param = IntegerParam(str(gxparam.flat_name))
        param.value = gxparam.value
        param.min = gxparam.min
        param.max = gxparam.max
        return param

    def init_float_param(self, gxparam: GalaxyParam) -> FloatParam:
        param = FloatParam(str(gxparam.flat_name))
        param.value = gxparam.value
        param.min = gxparam.min
        param.max = gxparam.max
        return param

    def init_bool_param(self, gxparam: GalaxyParam) -> BoolParam:
        param = BoolParam(str(gxparam.flat_name))
        param.checked = bool(gxparam.checked)
        param.truevalue = str(gxparam.truevalue)
        param.falsevalue = str(gxparam.falsevalue)
        return param

    def init_select_param(self, gxparam: GalaxyParam) -> SelectParam:
        param = SelectParam(str(gxparam.flat_name))
        param.multiple = bool(gxparam.multiple)
        param.options = [   SelectOption(value=opt[1], selected=opt[2], ui_text=opt[0]) 
                            for opt in gxparam.static_options]
        return param

    def init_data_param(self, gxparam: GalaxyParam) -> DataParam:
        param = DataParam(str(gxparam.flat_name))
        param.datatypes = gxparam.extensions
        param.multiple = bool(gxparam.multiple)
        return param

    def init_data_collection_param(self, gxparam: GalaxyParam) -> DataCollectionParam:
        param = DataCollectionParam(str(gxparam.flat_name))
        param.datatypes = gxparam.extensions
        return param

