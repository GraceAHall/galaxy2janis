


from command.components.outputs.UnknownOutput import UnknownOutput
from datatypes.DatatypeRegister import DatatypeRegister
from datatypes.JanisDatatype import JanisDatatype
from command.components.inputs import Positional, Flag, Option
from command.components.outputs import RedirectOutput, InputOutput, WildcardOutput
from workflows.io.WorkflowInput import WorkflowInput
from workflows.step.WorkflowStep import WorkflowStep
from workflows.io.WorkflowOutput import WorkflowOutput

from datatypes.default import DEFAULT_DATATYPE

def positional_strategy(positional: Positional, register: DatatypeRegister) -> None:
    gxtypes: list[str] = []
    if positional.gxparam:
        gxtypes = positional.gxparam.datatypes
    elif positional.value_record.values_are_ints():
        gxtypes = ['integer']
    elif positional.value_record.values_are_floats():
        gxtypes = ['float']
    positional.janis_datatypes = cast_gx_to_janis(gxtypes, register)

def flag_strategy(flag: Flag, register: DatatypeRegister) -> None:
    gxtypes = ['boolean']
    flag.janis_datatypes = cast_gx_to_janis(gxtypes, register)

def option_strategy(option: Option, register: DatatypeRegister) -> None:
    gxtypes: list[str] = []
    if option.gxparam:
        gxtypes = option.gxparam.datatypes
    elif option.value_record.values_are_ints():
        gxtypes = ['integer']
    elif option.value_record.values_are_floats():
        gxtypes = ['float']
    option.janis_datatypes = cast_gx_to_janis(gxtypes, register)

def redirect_output_strategy(redirect_output: RedirectOutput, register: DatatypeRegister) -> None:
    gxtypes: list[str] = []
    if redirect_output.gxparam:
        gxtypes = redirect_output.gxparam.datatypes
    redirect_output.janis_datatypes = cast_gx_to_janis(gxtypes, register)

def input_output_strategy(input_output: InputOutput, register: DatatypeRegister) -> None:
    gxtypes: list[str] = []
    if input_output.gxparam:
        gxtypes = input_output.gxparam.datatypes
    input_output.janis_datatypes = cast_gx_to_janis(gxtypes, register)

def wildcard_output_strategy(wildcard_output: WildcardOutput, register: DatatypeRegister) -> None:
    gxtypes: list[str] = []
    if wildcard_output.gxparam:
        gxtypes = wildcard_output.gxparam.datatypes
    wildcard_output.janis_datatypes = cast_gx_to_janis(gxtypes, register)

def workflow_input_strategy(inp: WorkflowInput, register: DatatypeRegister) -> None:
    inp.janis_datatypes = cast_gx_to_janis(inp.gx_datatypes, register)

def tool_step_strategy(tool_step: WorkflowStep, register: DatatypeRegister) -> None:
    for output in tool_step.outputs.list():
        output.janis_datatypes = cast_gx_to_janis(output.gx_datatypes, register)

def workflow_output_strategy(output: WorkflowOutput, register: DatatypeRegister) -> None:
    output.janis_datatypes = cast_gx_to_janis(output.gx_datatypes, register)

def cast_gx_to_janis(gxtypes: list[str], register: DatatypeRegister) -> list[JanisDatatype]:
    out: list[JanisDatatype] = []
    for gxtype in gxtypes:
        jtype = register.get(gxtype)
        if jtype is not None:
            out.append(jtype)
    if len(out) == 0:
        out.append(DEFAULT_DATATYPE)
    return out

strategy_map = {
    Positional: positional_strategy,
    Flag: flag_strategy,
    Option: option_strategy,
    RedirectOutput: redirect_output_strategy,
    InputOutput: input_output_strategy,
    WildcardOutput: wildcard_output_strategy,
    UnknownOutput: wildcard_output_strategy,
    WorkflowInput: workflow_input_strategy,
    WorkflowStep: tool_step_strategy,
    WorkflowOutput: workflow_output_strategy,
}


AnnotatableConstructs = Positional | Flag | Option | RedirectOutput | InputOutput | WildcardOutput | WorkflowInput | WorkflowStep | WorkflowOutput

class DatatypeAnnotator:
    def __init__(self) -> None:
        self.datatype_register = DatatypeRegister()

    def annotate(self, construct: AnnotatableConstructs) -> None:
        annotation_strategy = strategy_map[type(construct)]  
        annotation_strategy(construct, self.datatype_register)





        
