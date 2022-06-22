
from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from shellparser.components.inputs import Positional, Flag, Option
    from shellparser.components.outputs import RedirectOutput, InputOutput, WildcardOutput
    from entities.workflow.input import WorkflowInput
    from entities.workflow.workflow import WorkflowStep
    from entities.workflow.output import WorkflowOutput

from .default import DEFAULT_DATATYPE
from .janis import JanisDatatype
from .register import register


def cast_gx_to_janis(gxtypes: list[str]) -> list[JanisDatatype]:
    out: list[JanisDatatype] = []
    for gxtype in gxtypes:
        jtype = register.get(gxtype)
        if jtype is not None:
            out.append(jtype)
    if len(out) == 0:
        out.append(DEFAULT_DATATYPE)
    return out

def positional_strategy(positional: Positional) -> None:
    gxtypes: list[str] = []
    if positional.gxparam:
        gxtypes = positional.gxparam.datatypes
    elif positional.value_record.values_are_ints():
        gxtypes = ['integer']
    elif positional.value_record.values_are_floats():
        gxtypes = ['float']
    positional.janis_datatypes = cast_gx_to_janis(gxtypes)

def flag_strategy(flag: Flag) -> None:
    gxtypes = ['boolean']
    flag.janis_datatypes = cast_gx_to_janis(gxtypes)

def option_strategy(option: Option) -> None:
    gxtypes: list[str] = []
    if option.gxparam:
        gxtypes = option.gxparam.datatypes
    elif option.value_record.values_are_ints():
        gxtypes = ['integer']
    elif option.value_record.values_are_floats():
        gxtypes = ['float']
    option.janis_datatypes = cast_gx_to_janis(gxtypes)

def redirect_output_strategy(redirect_output: RedirectOutput) -> None:
    gxtypes: list[str] = []
    if redirect_output.gxparam:
        gxtypes = redirect_output.gxparam.datatypes
    redirect_output.janis_datatypes = cast_gx_to_janis(gxtypes)

def input_output_strategy(input_output: InputOutput) -> None:
    gxtypes: list[str] = []
    if input_output.gxparam:
        gxtypes = input_output.gxparam.datatypes
    input_output.janis_datatypes = cast_gx_to_janis(gxtypes)

def wildcard_output_strategy(wildcard_output: WildcardOutput) -> None:
    gxtypes: list[str] = []
    if wildcard_output.gxparam:
        gxtypes = wildcard_output.gxparam.datatypes
    wildcard_output.janis_datatypes = cast_gx_to_janis(gxtypes)

def workflow_input_strategy(inp: WorkflowInput) -> None:
    inp.janis_datatypes = cast_gx_to_janis(inp.gx_datatypes)

def tool_step_strategy(tool_step: WorkflowStep) -> None:
    for output in tool_step.outputs.list():
        output.janis_datatypes = cast_gx_to_janis(output.gx_datatypes)

def workflow_output_strategy(output: WorkflowOutput) -> None:
    output.janis_datatypes = cast_gx_to_janis(output.gx_datatypes)

strategy_map = {
    'Positional': positional_strategy,
    'Flag': flag_strategy,
    'Option': option_strategy,
    'RedirectOutput': redirect_output_strategy,
    'InputOutput': input_output_strategy,
    'WildcardOutput': wildcard_output_strategy,
    'UncertainOutput': wildcard_output_strategy,
    'WorkflowInput': workflow_input_strategy,
    'WorkflowStep': tool_step_strategy,
    'WorkflowOutput': workflow_output_strategy,
}


def annotate(entity: Any) -> None:
    entity_type = entity.__class__.__name__
    strategy = strategy_map[entity_type]  
    strategy(entity)



        
