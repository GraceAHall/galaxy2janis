
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shellparser.components.inputs import Positional, Flag, Option
    from shellparser.components.outputs import RedirectOutput, InputOutput, WildcardOutput
    from entities.workflow import WorkflowInput
    from entities.workflow import WorkflowOutput


def positional_strategy(positional: Positional) -> list[str]:
    gxtypes: list[str] = []
    if positional.gxparam:
        gxtypes = positional.gxparam.datatypes
    elif positional.value_record.values_are_ints():
        gxtypes = ['integer']
    elif positional.value_record.values_are_floats():
        gxtypes = ['float']
    return gxtypes

def flag_strategy(flag: Flag) -> list[str]:
    return ['boolean']

def option_strategy(option: Option) -> list[str]:
    gxtypes: list[str] = []
    if option.gxparam:
        gxtypes = option.gxparam.datatypes
    elif option.value_record.values_are_ints(): # TODO bad
        gxtypes = ['integer']
    elif option.value_record.values_are_floats():
        gxtypes = ['float']
    return gxtypes

def redirect_output_strategy(redirect_output: RedirectOutput) -> list[str]:
    gxtypes: list[str] = []
    if redirect_output.gxparam:
        gxtypes = redirect_output.gxparam.datatypes
    return gxtypes

def input_output_strategy(input_output: InputOutput) -> list[str]: # ???
    gxtypes: list[str] = []
    if input_output.gxparam:
        gxtypes = input_output.gxparam.datatypes
    return gxtypes

def wildcard_output_strategy(wildcard_output: WildcardOutput) -> list[str]:
    gxtypes: list[str] = []
    if wildcard_output.gxparam:
        gxtypes = wildcard_output.gxparam.datatypes
    return gxtypes

def workflow_input_strategy(inp: WorkflowInput) -> list[str]:
    return inp.gx_datatypes

def workflow_output_strategy(output: WorkflowOutput) -> list[str]:
    return output.gx_datatypes

strategy_map = {
    'Positional': positional_strategy,
    'Flag': flag_strategy,
    'Option': option_strategy,
    'RedirectOutput': redirect_output_strategy,
    'InputOutput': input_output_strategy,
    'WildcardOutput': wildcard_output_strategy,
    'UncertainOutput': wildcard_output_strategy,
    'WorkflowInput': workflow_input_strategy,
    'WorkflowOutput': workflow_output_strategy,
}





        
