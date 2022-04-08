


from datatypes.DatatypeRegister import DatatypeRegister
from datatypes.JanisDatatype import JanisDatatype
from command.components.inputs import Positional, Flag, Option
from command.components.outputs import RedirectOutput, InputOutput, WildcardOutput
from workflows.step.WorkflowStep import InputDataStep, ToolStep
from workflows.io.WorkflowOutput import WorkflowOutput

FALLBACK = JanisDatatype(
    format='file',
    source='janis',
    classname='File',
    extensions=None,
    import_path='janis_core.types.common_data_types'
)

def positional_strategy(positional: Positional, register: DatatypeRegister) -> None:
    gxtypes: list[str] = []
    if positional.gxparam:
        gxtypes = positional.gxparam.datatypes
    elif positional.value_record.values_are_ints():
        gxtypes = ['integer']
    elif positional.value_record.values_are_floats():
        gxtypes = ['float']
    else:
        gxtypes = ['file']
    positional.janis_datatypes = [cast_gx_to_janis(gx, register) for gx in gxtypes]

def flag_strategy(flag: Flag, register: DatatypeRegister) -> None:
    flag.janis_datatypes = [cast_gx_to_janis('boolean', register)]

def option_strategy(option: Option, register: DatatypeRegister) -> None:
    gxtypes: list[str] = []
    if option.gxparam:
        gxtypes = option.gxparam.datatypes
    elif option.value_record.values_are_ints():
        gxtypes = ['integer']
    elif option.value_record.values_are_floats():
        gxtypes = ['float']
    else:
        gxtypes = ['file']
    option.janis_datatypes = [cast_gx_to_janis(gx, register) for gx in gxtypes]

def redirect_output_strategy(redirect_output: RedirectOutput, register: DatatypeRegister) -> None:
    gxtypes: list[str] = []
    if redirect_output.gxparam:
        gxtypes = redirect_output.gxparam.datatypes
    else:
        gxtypes = ['file']
    redirect_output.janis_datatypes = [cast_gx_to_janis(gx, register) for gx in gxtypes]

def input_output_strategy(input_output: InputOutput, register: DatatypeRegister) -> None:
    gxtypes: list[str] = []
    if input_output.gxparam:
        gxtypes = input_output.gxparam.datatypes
    else:
        gxtypes = ['file']
    input_output.janis_datatypes = [cast_gx_to_janis(gx, register) for gx in gxtypes]

def wildcard_output_strategy(wildcard_output: WildcardOutput, register: DatatypeRegister) -> None:
    gxtypes: list[str] = []
    if wildcard_output.gxparam:
        gxtypes = wildcard_output.gxparam.datatypes
    else:
        gxtypes = ['file']
    wildcard_output.janis_datatypes = [cast_gx_to_janis(gx, register) for gx in gxtypes]

def input_data_step_strategy(input_step: InputDataStep, register: DatatypeRegister) -> None:
    gx_datatypes = input_step.metadata.gx_datatypes
    janis_datatypes = [cast_gx_to_janis(gx, register) for gx in gx_datatypes]
    input_step.metadata.janis_datatypes = [cast_gx_to_janis(gx, register) for gx in gx_datatypes]
    for output in input_step.output_register.list_outputs():
        output.janis_datatypes = janis_datatypes

def tool_step_strategy(tool_step: ToolStep, register: DatatypeRegister) -> None:
    for output in tool_step.output_register.list_outputs():
        output.janis_datatypes = [cast_gx_to_janis(gx, register) for gx in output.gx_datatypes]

def workflow_output_strategy(output: WorkflowOutput, register: DatatypeRegister) -> None:
    output.janis_datatypes = [cast_gx_to_janis(gx, register) for gx in output.gx_datatypes]

def cast_gx_to_janis(gxtype: str, register: DatatypeRegister) -> JanisDatatype:
    jtype = register.get(gxtype)
    if jtype is None:
        jtype = FALLBACK 
    return jtype


strategy_map = {
    Positional: positional_strategy,
    Flag: flag_strategy,
    Option: option_strategy,
    RedirectOutput: redirect_output_strategy,
    InputOutput: input_output_strategy,
    WildcardOutput: wildcard_output_strategy,
    InputDataStep: input_data_step_strategy,
    ToolStep: tool_step_strategy,
    WorkflowOutput: workflow_output_strategy,
}


AnnotatableConstructs = Positional | Flag | Option | RedirectOutput | InputOutput | WildcardOutput | InputDataStep | ToolStep | WorkflowOutput

class DatatypeAnnotator:
    def __init__(self) -> None:
        self.datatype_register = DatatypeRegister()

    def annotate(self, construct: AnnotatableConstructs) -> None:
        annotation_strategy = strategy_map[type(construct)]  
        annotation_strategy(construct, self.datatype_register)





        
