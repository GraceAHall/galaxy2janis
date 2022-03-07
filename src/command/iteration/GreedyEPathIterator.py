

from copy import deepcopy
from typing import Iterable, Optional, Tuple
from command.cmdstr.ExecutionPath import ExecutionPath
from command.tokens.Tokens import Token, TokenType
import command.iteration.utils as component_utils
from command.iteration.ComponentSpawner import spawn_component
from command.components.CommandComponent import CommandComponent

"""
iterates through a DynamicCommandString, yielding the current tokens being assessed.
keeps track of the location we are in the DynamicCommandString

Example DynamicCommandString:
abricate $sample_name --no-header --minid=80 --db = card

0           1             2            3           4          5        6           7          8
abricate    $sample_name  --no-header  --minid     =          80       --db        =          card
RAW_STRING  ENV_VAR       RAW_STRING   RAW_STRING  KV_LINKER  RAW_INT  RAW_STRING  KV_LINKER  RAW_STRING

at token 2, we would return {
    ctoken: token 2  (--no-header's token),
    ntokens: []
}
at token 3, we would return {
    ctoken: token 3 (--minid's token),
    ntokens: [token 4, token 5]
}

"""



class GreedyEPathIterator:
    def __init__(self, epath: ExecutionPath):
        self.epath = epath 
        self.pos = 0
    
    def iter(self) -> Iterable[CommandComponent]:
        self.pos = 0 # reset
        while self.pos < len(self.epath.tokens) - 1:
            if not self.epath.tokens[self.pos].type == TokenType.EXCISION:
                start, stop, component = self.fetch()
                yield component
            self.pos += 1

    def search(self, query: str) -> Optional[CommandComponent]:
        self.pos = 0 # reset
        while self.pos < len(self.epath.tokens) - 1:
            if self.epath.tokens[self.pos].text == query:
                start, stop, component = self.fetch()
                self.epath.excise_tokens(list(range(start, stop)))
                return component
            self.pos += 1
    
    def fetch(self) -> Tuple[int, int, CommandComponent]:
        """
        creates a component starting at the current position in the epath
        returns the start location and stop location for the component
        ie 
            if its a flag, will be self.pos, self.pos + 1, component
            if its an option with 2 values, will be self.pos, self.pos + 3, component
        """
        start = deepcopy(self.pos) # current position we are looking at
        ctoken = self.epath.tokens[self.pos]
        ntoken = self.epath.tokens[self.pos + 1]

        comp: str = ''
        delim: str = ''
        vtokens: list[Token] = []

        if component_utils.is_option(ctoken, ntoken):
            comp = 'option'
            delim, vtokens = self.format_option()
        elif component_utils.is_flag(ctoken, ntoken):
            comp = 'flag'
        else:
            comp = 'positional'

        stop = self.pos + 1
        component = spawn_component(comp, ctoken, vtokens, epath_id=self.epath.id, delim=delim)
        self.annotate_gxvar(start, stop, component)
        return start, stop, component

    def format_option(self) -> Tuple[str, list[Token]]:
        delim = self.get_delim()
        value_tokens = self.get_option_values()
        return delim, value_tokens

    def get_delim(self) -> str:
        if self.epath.tokens[self.pos + 1].type == TokenType.KV_LINKER:
            self.pos += 1
            return self.epath.tokens[self.pos].text
        return ' '

    def get_option_values(self) -> list[Token]:
        out: list[Token] = []
        values_type = self.epath.tokens[self.pos + 1].type
        ntoken = self.epath.tokens[self.pos + 1]
        # look at next ntoken to see its probably a value for the option
        while component_utils.is_positional(ntoken) and ntoken.type == values_type:
            out.append(ntoken)
            self.pos += 1
            ntoken = self.epath.tokens[self.pos + 1]
        return out

    def annotate_gxvar(self, start: int, stop: int, component: CommandComponent) -> None:
        for i in range(start, stop):
            if self.epath.tokens[i].gxvar:
                component.gxvar = self.epath.tokens[i].gxvar
                break



