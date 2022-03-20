

from typing import Tuple
from .RedirectOutput import RedirectOutput
from .InputOutput import InputOutput
from .WildcardOutput import WildcardOutput

from command.tokens.Tokens import Token
from command.components.CommandComponent import CommandComponent
from xmltool.param.Param import Param


class OutputComponentFactory:
    def create_redirect_output(self, tokens: Tuple[Token, Token]) -> RedirectOutput:
        return RedirectOutput(tokens)
    
    def create_input_output(self, input_component: CommandComponent) -> InputOutput:
        return InputOutput(input_component)
    
    def create_wildcard_output(self, gxparam: Param) -> WildcardOutput:
        return WildcardOutput(gxparam)


# class OutputComponentFactory:
#     def create(self, subtype: str, incoming: Any) -> CommandComponent:
#         match incoming:
#             case [Token(), Token()]:
#                 return self.create_redirect_output(incoming)
#             case CommandComponent():
#                 return self.create_input_output(incoming)
#             case OutputParam():
#                 return self.create_wildcard_output(incoming)
#             case _:
#                 raise RuntimeError()