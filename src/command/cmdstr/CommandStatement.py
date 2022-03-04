

from typing import Iterable, Optional

from tool.tool_definition import GalaxyToolDefinition
from command.tokens.Tokens import Token
from command.tokens.CommandTokenifier import CommandTokenifier
from command.cmdstr.ExecutionPath import ExecutionPath


class CommandStatement:
    def __init__(self, cmdline: str, end_delim: Optional[str]=None):
        self.cmdline = cmdline
        self.end_delim = end_delim
        self.tokens: list[list[Token]] = []
        # features 

    def set_tokens(self, tool: GalaxyToolDefinition) -> None:
        self.tokens = CommandTokenifier(tool).tokenify(self.cmdline)

    def get_execution_paths(self) -> Iterable[ExecutionPath]:
        raise NotImplementedError
        # cword_vals = self.cword.get_values()
        # nword_vals = self.nword.get_values()
        # for cval in cword_vals:
        #     for nval in nword_vals:
        #         cwords = self.wordifier.wordify(cval)
        #         nwords = self.wordifier.wordify(nval)
        #         # okay this looks mental but its just returning
        #         # the current cval CommandWords, and the first CommandWord
        #         # from nval, plus a sentinel on the end
        #         sentinel = cwords[-1]
        #         yield cwords[:-1] + [nwords[0]] + [sentinel]
    


