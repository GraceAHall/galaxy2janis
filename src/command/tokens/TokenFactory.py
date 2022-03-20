

from abc import ABC, abstractmethod

from command.tokens.Tokens import Token, TokenType
from command.regex import scanners as scanners
from command.regex.utils import get_base_variable
from xmltool.tool_definition import XMLToolDefinition


class TokenOrderingStrategy(ABC):
    @abstractmethod
    def order(self, token_list: list[Token]) -> list[Token]:
        """selects a token in the list according to some prioritisation"""
        ...


class FirstTokenOrderingStrategy(TokenOrderingStrategy):
    def order(self, token_list: list[Token]) -> list[Token]:
        """selects a token in the list according to some prioritisation"""
        token_list.sort(key=lambda x: x.start)
        return token_list


class LongestTokenOrderingStrategy(TokenOrderingStrategy):
    def order(self, token_list: list[Token]) -> list[Token]:
        """selects a token in the list according to some prioritisation"""
        token_list.sort(key=lambda x: x.end - x.start)
        return token_list


class PriorityTokenOrderingStrategy(TokenOrderingStrategy):
    def order(self, token_list: list[Token]) -> list[Token]:
        priorities: dict[TokenType, int] = {
            TokenType.GX_KW_DYNAMIC: 1,
            TokenType.GX_KW_STATIC: 2,
            TokenType.KV_PAIR: 3,
            TokenType.KV_LINKER: 3,
            TokenType.GX_INPUT: 4,
            TokenType.GX_OUTPUT: 4,
            TokenType.ENV_VAR: 5,
            TokenType.QUOTED_STRING: 6,
            TokenType.QUOTED_NUM: 6,
            TokenType.RAW_STRING: 6,
            TokenType.RAW_NUM: 6,
            TokenType.LINUX_TEE: 6,
            TokenType.LINUX_REDIRECT: 6,
            TokenType.LINUX_STREAM_MERGE: 6,
            TokenType.UNKNOWN: 999,
        }
        token_list.sort(key=lambda x: priorities[x.type])
        return token_list


class TokenFactory:
    def __init__(self, xmltool: XMLToolDefinition):
        self.xmltool = xmltool    
        self.generic_scanners = [
            (scanners.get_keyval_pairs, TokenType.KV_PAIR),
            (scanners.get_quoted_numbers, TokenType.QUOTED_NUM),
            (scanners.get_quoted_strings, TokenType.QUOTED_STRING),
            (scanners.get_raw_numbers, TokenType.RAW_NUM),
            (scanners.get_raw_strings, TokenType.RAW_STRING),
            (scanners.get_redirects, TokenType.LINUX_REDIRECT),
            (scanners.get_tees, TokenType.LINUX_TEE),
            (scanners.get_stream_merges, TokenType.LINUX_STREAM_MERGE),
            (scanners.get_dynamic_keywords, TokenType.GX_KW_DYNAMIC),
            (scanners.get_static_keywords, TokenType.GX_KW_STATIC),
            (scanners.get_all, TokenType.UNKNOWN)
        ]
        self.ordering_strategies: dict[str, TokenOrderingStrategy] = {
            'first':  FirstTokenOrderingStrategy(),
            'priority':  PriorityTokenOrderingStrategy(),
            'longest':  LongestTokenOrderingStrategy()
        }

    def spawn_end_sentinel(self) -> Token:
        matches = scanners.get_all('end')
        return Token(matches[0], TokenType.END_STATEMENT)

    def spawn_kv_linker(self, delim: str) -> Token:
        matches = scanners.get_all(delim)
        return Token(matches[0], TokenType.KV_LINKER)

    def create(self, word: str, prioritisation: str='priority') -> Token:
        """
        extracts the best token from a word.
        where multiple token types are possible, selection can be made 
        """
        if word == '${GALAXY_SLOTS:-2}':
            print()
        token_list = self.get_all_tokens(word)
        token_list = self.perform_default_ordering(token_list)
        final_ordering = self.perform_final_ordering(token_list, prioritisation)
        final_token = final_ordering[0]
        return final_token

    def perform_default_ordering(self, token_list: list[Token]) -> list[Token]:
        #default orderings (low to high priority) first, longest, priority
        for strategy in self.ordering_strategies.values():
            token_list = strategy.order(token_list)
        return token_list
        
    def perform_final_ordering(self, token_list: list[Token],  prioritisation: str) -> list[Token]:
        # overriding final prioritisation
        return self.ordering_strategies[prioritisation].order(token_list)

    def get_all_tokens(self, the_string: str) -> list[Token]:
        """gets all the possible token interpretations of the_string"""  
        tokens: list[Token] = []
        tokens += self.get_generic_tokens(the_string)
        tokens += self.get_variable_tokens(the_string)
        return tokens

    def get_generic_tokens(self, the_string: str) -> list[Token]:
        """gets all tokens except galaxy/env variables"""
        tokens: list[Token] = []
        for scanner_func, ttype in self.generic_scanners:
            matches = scanner_func(the_string)
            tokens += [Token(m, ttype) for m in matches]
        return tokens

    def get_variable_tokens(self, the_string: str) -> list[Token]:
        """gets tokens for galaxy/env variables"""
        tokens: list[Token] = []
        matches = scanners.get_variables(the_string)
        base_vars = [get_base_variable(m) for m in matches]
        
        for m, varname in zip(matches, base_vars):
            if varname:
                if self.xmltool.get_input(varname):
                    tokens.append(Token(m, TokenType.GX_INPUT, gxparam=self.xmltool.get_input(varname)))
                elif self.xmltool.get_output(varname):
                    tokens.append(Token(m, TokenType.GX_OUTPUT, gxparam=self.xmltool.get_output(varname)))
                else:
                    tokens.append(Token(m, TokenType.ENV_VAR))
        return tokens
    
    