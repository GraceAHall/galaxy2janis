




from typing import Optional


from tool.tool_definition import GalaxyToolDefinition
from tool.param.Param import Param

from command.cmdstr.ConstructTracker import ConstructTracker
from command.cmdstr.utils import split_lines, split_to_words
from command.tokens.Tokens import Token, TokenType
from command.tokens.TokenFactory import TokenFactory
from command.iteration.utils import is_bool_select


class RealisedTokenValues:
    def __init__(self, values: list[list[Token]], original: Optional[Token]=None):
        self.tlists = values
        if original:
            self.set_context_from_original_token(original)
        
    def set_context_from_original_token(self, source: Token) -> None:
        for tlist in self.tlists:
            for token in tlist:
                token.gxvar = source.gxvar
                token.in_conditional = source.in_conditional
                token.in_loop = source.in_loop

    def set_levels(self, levels: dict[str, int]) -> None:
        for tlist in self.tlists:
            for token in tlist:
                if levels:
                    if levels['conditional'] > 0:
                        token.in_conditional = True
                    if levels['loop'] > 0:
                        token.in_loop = True
    
    def get_default_token(self) -> Token:
        return self.tlists[0][0]
    
    def get_first_word(self) -> str:
        return self.tlists[0][0].text

    def get_gx_reference(self) -> Optional[Param]:
        # every token will have the same gx object
        return self.get_default_token().gxvar
    
    def __repr__(self) -> str:
        strvalues: list[str] = []
        for tlist in self.tlists:
            strvalues.append(' '.join([token.text for token in tlist]))
        return f'RealisedTokenValues: {", ".join(strvalues)}'



class RealisedTokenValueifier:
    def __init__(self, tool: GalaxyToolDefinition):
        self.tracker = ConstructTracker()
        self.factory = TokenFactory(tool)
        self.tokens: list[RealisedTokenValues] = []

    def tokenify(self, the_string: str) -> list[RealisedTokenValues]:
        self.refresh_attrs()
        for line in split_lines(the_string):
            self.handle_line(line)
        return self.tokens

    def refresh_attrs(self) -> None:
        self.tracker = ConstructTracker()
        self.tokens = []

    def handle_line(self, line: str) -> None:
        self.tracker.update(line)
        if self.tracker.should_tokenify_line(line):
            token_lists = self.tokenify_line(line)
            realised_token_values = self.get_realised_values(token_lists)
            for rtvs in realised_token_values:
                rtvs.set_levels(self.tracker.get_levels())
            self.tokens += realised_token_values
    
    def tokenify_line(self, line: str) -> list[Token]:
        words = split_to_words(line)
        tokens = [self.factory.create(text) for text in words]
        tokens = self.expand_kvpairs(tokens)
        return tokens

    def expand_kvpairs(self, tokens: list[Token]) -> list[Token]:
        out: list[Token] = []
        for token in tokens:
            if token.type == TokenType.KV_PAIR:
                out += self.split_kv_token(token)
            else:
                out.append(token)
        return out

    def split_kv_token(self, token: Token) -> list[Token]:
        left_text = str(token.match.group(1))
        delim = str(token.match.group(2))
        right_text = str(token.match.group(3))
        return [
            self.factory.create(left_text),
            self.factory.spawn_kv_linker(delim),
            self.factory.create(right_text)
        ]

    def get_realised_values(self, tokens: list[Token]) -> list[RealisedTokenValues]:
        out: list[RealisedTokenValues] = []
        for token in tokens:
            if is_bool_select(token):
                vals_as_text: list[str] = token.gxvar.get_all_values(nonempty=True) #type: ignore
                vals_as_tlists = [self.tokenify_line(text) for text in vals_as_text]
                out.append(RealisedTokenValues(values=vals_as_tlists, original=token))
            else:
                out.append(RealisedTokenValues(values=[[token]], original=token))
        return out

        

