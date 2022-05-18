

from typing import Any, Tuple
from .RedirectOutput import RedirectOutput
from .InputOutput import InputOutput
from .WildcardOutput import WildcardOutput
from .UnknownOutput import UnknownOutput

from command.text.tokens.Tokens import Token
from command.components.CommandComponent import CommandComponent
from xmltool.param.Param import Param


# acts as a factory

def create_redirect_output(tokens: Tuple[Token, Token]) -> RedirectOutput:
    return RedirectOutput(tokens)

def create_input_output(input_component: CommandComponent) -> InputOutput:
    return InputOutput(input_component)

def create_wildcard_output(gxparam: Param) -> WildcardOutput:
    output = WildcardOutput()
    output.gxparam = gxparam
    return output

def create_unknown_output(gxparam: Param) -> UnknownOutput:
    output = UnknownOutput()
    output.gxparam = gxparam
    return output

output_map = {
    'redirect': create_redirect_output,
    'input': create_input_output,
    'wildcard': create_wildcard_output,
    'unknown': create_unknown_output
}

def create_output(ctype: str, incoming: Any) -> CommandComponent:
    strategy = output_map[ctype]
    return strategy(incoming)


