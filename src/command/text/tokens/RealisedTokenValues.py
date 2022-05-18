




from typing import Optional

from xmltool.param.Param import Param

from command.cheetah.ConstructTracker import ConstructTracker
from command.cmdstr.utils import split_lines, split_to_words
from command.text.tokens.Tokens import Token
from command.text.tokens.TokenFactory import TokenFactory
from command.epath.utils import is_bool_select

class RealisedTokenValues:
    """
    class exists to expose hidden values within galaxy params
    each galaxy select param can hold any number of text values,
    and each text value may have 1 or more words / keyval pairs
    """
    def __init__(self, values: list[list[Token]], original: Token):
        self.tlists = values
        self.original = original
        if original:
            self.set_context_from_original_token(original)
        
    def set_context_from_original_token(self, source: Token) -> None:
        for tlist in self.tlists:
            for token in tlist:
                token.gxparam = source.gxparam
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

    def get_original_token(self) -> Token:
        return self.original
    
    def get_default_token(self) -> Token:
        for tlist in self.tlists:
            if len(tlist) > 0:
                return tlist[0]
        return self.get_original_token()
    
    def get_first_word(self) -> str:
        return self.get_default_token().text

    def get_gx_reference(self) -> Optional[Param]:
        # every token will have the same gx object
        return self.get_original_token().gxparam
    
    def __repr__(self) -> str:
        strvalues: list[str] = []
        for tlist in self.tlists:
            strvalues.append(' '.join([token.text for token in tlist]))
        return f'RealisedTokenValues: {", ".join(strvalues)}'



class RealisedTokenValueifier:
    def __init__(self, token_factory: TokenFactory):
        self.factory = token_factory
        self.tracker = ConstructTracker()
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
        if self.should_tokenify_line(line):
            token_lists = self.tokenify_line(line)
            realised_token_values = self.get_realised_values(token_lists)
            for rtvs in realised_token_values:
                rtvs.set_levels(self.tracker.get_levels())
            self.tokens += realised_token_values

    def should_tokenify_line(self, line: str) -> bool:
        if self.tracker.is_construct_line(line) or self.tracker.within_banned_segment():
            return False
        return True
    
    def tokenify_line(self, line: str) -> list[Token]:
        words = split_to_words(line)
        tokens: list[Token] = []
        for word in words:
            tokens += self.tokenify_word(word)
        return tokens

    def tokenify_word(self, text: str) -> list[Token]:
        return self.factory.create(text)

        # def expand_kvpairs(self, tokens: list[Token]) -> list[Token]:
    #     out: list[Token] = []
    #     for token in tokens:
    #         if token.type == TokenType.KV_PAIR:
    #             out += self.split_kv_token(token)
    #         else:
    #             out.append(token)
    #     return out

    # def split_kv_token(self, token: Token) -> list[Token]:
    #     left_text = str(token.match.group(1))
    #     delim = str(token.match.group(2))
    #     right_text = str(token.match.group(3))
    #     return [
    #         self.factory.create(left_text),
    #         utils.spawn_kv_linker(delim),
    #         self.factory.create(right_text)
    #     ]

    def get_realised_values(self, tokens: list[Token]) -> list[RealisedTokenValues]:
        out: list[RealisedTokenValues] = []
        for token in tokens:
            if is_bool_select(token):
                vals_as_text: list[str] = token.gxparam.get_all_values(nonempty=True) #type: ignore
                vals_as_tlists = [self.tokenify_line(text) for text in vals_as_text]
                out.append(RealisedTokenValues(values=vals_as_tlists, original=token))
            else:
                out.append(RealisedTokenValues(values=[[token]], original=token))
        return out

        

