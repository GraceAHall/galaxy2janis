

from typing import Any, Tuple

from ...parser.tokens.Token import Token
from gx.gxtool.param.Param import Param

from .RedirectOutput import RedirectOutput
from .InputOutput import InputOutput
from .WildcardOutput import WildcardOutput
from ..CommandComponent import CommandComponent


# acts as a factory

def create_redirect_output(tokens: Tuple[Token, Token]) -> RedirectOutput:
    return RedirectOutput(tokens)

def create_input_output(input_component: CommandComponent) -> InputOutput:
    return InputOutput(input_component)

def create_wildcard_output(gxparam: Param) -> WildcardOutput:
    output = WildcardOutput()
    output.gxparam = gxparam
    return output

def create_uncertain_output(gxparam: Param) -> WildcardOutput:
    output = WildcardOutput()
    output.gxparam = gxparam
    output.verified = False
    return output

output_map = {
    'redirect': create_redirect_output,
    'input': create_input_output,
    'wildcard': create_wildcard_output,
    'uncertain_wildcard': create_uncertain_output
}

def create_output(ctype: str, incoming: Any) -> CommandComponent:
    strategy = output_map[ctype]
    return strategy(incoming)


