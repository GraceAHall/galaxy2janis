

from typing import Any, Tuple
from .RedirectOutput import RedirectOutput
from .InputOutput import InputOutput
from .WildcardOutput import WildcardOutput
from .UncertainOutput import UncertainOutput

from shellparser.text.tokens.Tokens import Token
from shellparser.components.CommandComponent import CommandComponent
from gx.xmltool.param.Param import Param


# acts as a factory

def create_redirect_output(tokens: Tuple[Token, Token]) -> RedirectOutput:
    return RedirectOutput(tokens)

def create_input_output(input_component: CommandComponent) -> InputOutput:
    return InputOutput(input_component)

def create_wildcard_output(gxparam: Param) -> WildcardOutput:
    output = WildcardOutput()
    output.gxparam = gxparam
    return output

def create_uncertain_output(gxparam: Param) -> UncertainOutput:
    output = UncertainOutput()
    output.gxparam = gxparam
    return output

output_map = {
    'redirect': create_redirect_output,
    'input': create_input_output,
    'wildcard': create_wildcard_output,
    'uncertain': create_uncertain_output
}

def create_output(ctype: str, incoming: Any) -> CommandComponent:
    strategy = output_map[ctype]
    return strategy(incoming)


