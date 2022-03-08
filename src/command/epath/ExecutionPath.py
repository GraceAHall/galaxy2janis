



from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Optional, Tuple

from command.tokens.Tokens import Token, TokenType
from command.components.linux_constructs import Tee, Redirect, StreamMerge
from command.regex import scanners as scanners
from command.components.CommandComponent import CommandComponent



@dataclass
class EPathPosition:
    ptr: int
    token: Token
    ignore: bool = False
    component: Optional[CommandComponent] = None


class ExecutionPath:
    id: int

    def __init__(self, tokens: list[Token]):
        self.positions: list[EPathPosition] = self.init_positions(tokens)
        self.stream_merges: list[StreamMerge] = []
        self.redirect: Optional[Redirect] = None
        self.tees: Optional[Tee] = None
        self.tokens_to_excise: list[int] = []
        self.set_attrs()

    def init_positions(self, tokens: list[Token]) -> list[EPathPosition]:
        return [EPathPosition(i, token) for i, token in enumerate(tokens)]

    def get_components(self) -> dict[int, CommandComponent]:
        out: dict[int, CommandComponent] = {}
        for position in self.positions:
            if position.component:
                out[position.ptr] = position.component
        return out

    def set_attrs(self) -> None:
        self.set_stream_merges()
        self.set_redirect()
        self.set_tee()
    
    def set_stream_merges(self) -> None:
        for position in self.positions:
            if position.token.type == TokenType.LINUX_STREAM_MERGE:
                self.handle_stream_merge(position)

    def handle_stream_merge(self, position: EPathPosition) -> None:
        sm = StreamMerge(position.token)
        self.stream_merges.append(sm)
        self.annotate_position_with_component(position.ptr, sm)

    def annotate_position_with_component(self, ptr: int, comp: Any) -> None:
        self.positions[ptr].ignore = True
        self.positions[ptr].component = comp
    
    def set_redirect(self) -> None:
        for position in self.positions:
            if position.token.type == TokenType.LINUX_REDIRECT:
                self.handle_redirect(position)
                break
    
    def handle_redirect(self, position: EPathPosition) -> None:
        """
        handles an identified redirect. 
        creates Redirect() and marks corresponding CommandWords for removal
        """
        ptr = position.ptr
        redirect_token = self.positions[ptr].token
        outfile_token = self.positions[ptr + 1].token

        if redirect_token and outfile_token:
            redirect = Redirect(redirect_token, outfile_token)
            self.redirect = redirect
            self.annotate_position_with_component(ptr, redirect)
            self.annotate_position_with_component(ptr + 1, redirect)
                    
    def set_tee(self) -> None:
        for position in self.positions:
            if position.token.type == TokenType.LINUX_TEE:
                self.handle_tee(position)
                break

    def handle_tee(self, position: EPathPosition) -> None:
        #tee = self.init_tee(position)
        tee = Tee()
        ptr = position.ptr
        next_text = self.positions[ptr + 1].token.text

        # tee opts
        while next_text.startswith('-'):
            ptr += 1
            token = self.positions[ptr].token
            tee.options.append(token)
            self.annotate_position_with_component(ptr, tee)
            next_text = self.positions[ptr + 1].token.text
        # tee files
        while ptr < len(self.positions):
            ptr += 1
            token = self.positions[ptr].token
            tee.files.append(token)
            self.annotate_position_with_component(ptr, tee)

        self.tee = tee

    def __str__(self) -> str:
        out: str = ''
        for position in self.positions:
            out += f'{str(position.ptr):<3}{position.token.text[:19]:<20}{position.token.type:<32}{str(type(position.component))[:49]:<50}\n'
        return out


"""


0            1             2            3           4          5        6           7          8
abricate     $sample_name  --no-header  --minid     =          80       --db        =          card
RAW_STRING   ENV_VAR       RAW_STRING   RAW_STRING  KV_LINKER  RAW_INT  RAW_STRING  KV_LINKER  RAW_STRING
positional1  positional2   flag1        option1     option1    option1  option2     option2    option2


0            1             2            3           4          5        6           7          8
abricate     $sample_name  --no-header  --minid     =          80       --db        =          card
RAW_STRING   ENV_VAR       RAW_STRING   RAW_STRING  KV_LINKER  RAW_INT  RAW_STRING  KV_LINKER  RAW_STRING
None         None          None         None        None       None     None        None       None


"""

    # def excise_tokens(self, elements: Optional[list[int]]=None) -> None:
    #     if not elements:
    #         elements = self.tokens_to_excise
    #     for ind in elements:
    #         matches = scanners.get_all('excision')
    #         self.tokens[ind] = Token(matches[0], TokenType.EXCISION)
    #     self.tokens_to_excise = []

