




from typing import Optional

from xmltool.param.Param import Param

from command.cheetah.ConstructTracker import ConstructTracker
from command.cmdstr.utils import split_lines, split_to_words
from command.text.tokens.Tokens import Token
from command.text.tokens.TokenFactory import TokenFactory
from command.epath.utils import is_bool_select

class RealisedTokens:
    """
    class exists to expose hidden values within galaxy params
    each galaxy select param can hold any number of text values,
    and each text value may have 1 or more words / keyval pairs
    """
    def __init__(self, values: list[list[Token]], original: Token):
        self.tlists = values
        self.original = original
        
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



class RealisedTokenFactory:
    def __init__(self, token_factory: TokenFactory):
        self.factory = token_factory
        self.tracker = ConstructTracker()  # this is all a bit ugly

    def tokenify(self, the_string: str) -> list[RealisedTokens]:
        rtvs: list[RealisedTokens] = []
        for line in split_lines(the_string):
            self.tracker.update(line)
            if self.should_tokenify_line(line):
                rtvs += self.tokenify_line(line)
        return rtvs

    def should_tokenify_line(self, line: str) -> bool:
        if self.tracker.active_is_boundary(line) or self.tracker.within_banned_segment:
            return False
        return True
    
    def tokenify_line(self, line: str) -> list[RealisedTokens]:
        line_tokens = self.create_line_tokens(line)
        line_tokens = self.set_token_context(line_tokens)
        return self.create_realised_values(line_tokens)

    def create_line_tokens(self, line: str) -> list[Token]:
        line_tokens: list[Token] = []
        for word in split_to_words(line):
            line_tokens += self.factory.create(word)
        return line_tokens

    def set_token_context(self, line_tokens: list[Token]) -> list[Token]:
        for token in line_tokens:
            token.construct = self.tracker.stack.current_construct
            token.in_conditional = self.tracker.within_conditional
            token.in_loop = self.tracker.within_loop
        return line_tokens

    def create_realised_values(self, line_tokens: list[Token]) -> list[RealisedTokens]:
        out: list[RealisedTokens] = []
        for token in line_tokens:
            if is_bool_select(token):
                vals_as_text: list[str] = token.gxparam.get_all_values(nonempty=True) #type: ignore
                vals_as_tlists = [self.create_line_tokens(text) for text in vals_as_text]
                out.append(RealisedTokens(values=vals_as_tlists, original=token))
            else:
                out.append(RealisedTokens(values=[[token]], original=token))
        return out






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

        

