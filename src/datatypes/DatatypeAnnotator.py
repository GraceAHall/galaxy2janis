


from datatypes.DatatypeRegister import DatatypeRegister
from command.components.CommandComponent import CommandComponent
from datatypes.JanisDatatype import JanisDatatype
from command.components.inputs import Positional, Flag, Option
from command.components.outputs import RedirectOutput, InputOutput, WildcardOutput

FALLBACK = JanisDatatype(
    format='file',
    source='janis',
    classname='File',
    extensions=None,
    import_path='janis_core.types.common_data_types'
)

def positional_strategy(positional: Positional) -> list[str]:
    gxtypes: list[str] = []
    if positional.gxparam:
        gxtypes = positional.gxparam.datatypes
    elif positional.value_record.values_are_ints():
        gxtypes = ['integer']
    elif positional.value_record.values_are_floats():
        gxtypes = ['float']
    else:
        gxtypes = ['file']
    return gxtypes

def flag_strategy(flag: Flag) -> list[str]:
    return ['boolean']

def option_strategy(option: Option) -> list[str]:
    gxtypes: list[str] = []
    if option.gxparam:
        gxtypes = option.gxparam.datatypes
    elif option.value_record.values_are_ints():
        gxtypes = ['integer']
    elif option.value_record.values_are_floats():
        gxtypes = ['float']
    else:
        gxtypes = ['file']
    return gxtypes

def redirect_output_strategy(redirect_output: RedirectOutput) -> list[str]:
    gxtypes: list[str] = []
    if redirect_output.gxparam:
        gxtypes = redirect_output.gxparam.datatypes
    else:
        gxtypes = ['file']
    return gxtypes

def input_output_strategy(input_output: InputOutput) -> list[str]:
    gxtypes: list[str] = []
    if input_output.gxparam:
        gxtypes = input_output.gxparam.datatypes
    else:
        gxtypes = ['file']
    return gxtypes

def wildcard_output_strategy(wildcard_output: WildcardOutput) -> list[str]:
    gxtypes: list[str] = []
    if wildcard_output.gxparam:
        gxtypes = wildcard_output.gxparam.datatypes
    else:
        gxtypes = ['file']
    return gxtypes


strategy_map = {
    Positional: positional_strategy,
    Flag: flag_strategy,
    Option: option_strategy,
    RedirectOutput: redirect_output_strategy,
    InputOutput: input_output_strategy,
    WildcardOutput: wildcard_output_strategy
}


class DatatypeAnnotator:
    def __init__(self) -> None:
        self.datatype_register = DatatypeRegister()

    def annotate(self, component: CommandComponent) -> None:
        strategy_func = strategy_map[type(component)]  # TODO why? 
        gx_types = strategy_func(component)
        janis_types = [self.cast_gx_to_janis(gx) for gx in gx_types]
        component.datatypes = janis_types

    def cast_gx_to_janis(self, gxtypes: str) -> JanisDatatype:
        jtype = self.datatype_register.get(gxtypes)
        if jtype is None:
            jtype = FALLBACK 
        return jtype



        
