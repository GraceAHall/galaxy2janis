




from typing import Optional
from tool.tool_definition import GalaxyToolDefinition

from command.cmdstr.ConstructTracker import ConstructTracker
from command.cmdstr.utils import split_lines, split_to_words
from command.tokens.Tokens import Token, TokenType
from command.tokens.TokenFactory import TokenFactory
from command.iterators.utils import is_bool_select

class CommandTokenifier:
    def __init__(self, tool: GalaxyToolDefinition):
        self.tracker = ConstructTracker()
        self.factory = TokenFactory(tool)
        self.tokens: list[list[Token]] = []

    def tokenify(self, the_string: str) -> list[list[Token]]:
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
            token_lists = self.expand_galaxy(token_lists)
            token_lists = self.set_levels(token_lists, self.tracker.get_levels())
            self.tokens += token_lists
    
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

    def expand_galaxy(self, tokens: list[Token]) -> list[list[Token]]:
        out: list[list[Token]] = []
        for token in tokens:
            if is_bool_select(token):
                vals_as_text: list[str] = token.gxvar.get_all_values(nonempty=True) #type: ignore
                vals_as_tlists = [self.tokenify_line(text) for text in vals_as_text]
                for tlist in vals_as_tlists:
                    for exp_token in tlist:
                        self.transfer_context(token, exp_token)
                        # TODO HERE ALMOST WORKING
                out.append(vals_as_tlists)
            else:
                out.append([token])
        return out
            
    def set_levels(self, token_lists: list[list[Token]], levels: Optional[dict[str, int]]) -> list[list[Token]]:
        for tlist in token_lists:
            for token in tlist:
                if levels:
                    if levels['conditional'] > 0:
                        token.in_conditional = True
                    if levels['loop'] > 0:
                        token.in_loop = True
        return token_lists
        
    def transfer_context(self, source: Token, dest: Token) -> Token:
        dest.gxvar = source.gxvar
        dest.in_conditional = source.in_conditional
        dest.in_loop = source.in_loop
        return dest



