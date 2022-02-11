

from abc import ABC, abstractmethod
from typing import Optional

from command.tokens.Tokens import Token, TokenType
from command.regex import scanners as scanners
from command.regex.utils import get_base_variable
from tool.tool_definition import GalaxyToolDefinition


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
            TokenType.KV_PAIR: 1,
            TokenType.GX_INPUT: 2,
            TokenType.GX_OUT: 2,
            TokenType.GX_KEYWORD: 3,
            TokenType.ENV_VAR: 3,
            TokenType.QUOTED_STRING: 4,
            TokenType.QUOTED_NUM: 4,
            TokenType.RAW_STRING: 4,
            TokenType.RAW_NUM: 4,
            TokenType.START_STATEMENT: 4,
            TokenType.END_STATEMENT: 4,
            TokenType.LINUX_TEE: 4,
            TokenType.LINUX_REDIRECT: 4,
            TokenType.LINUX_STREAM_MERGE: 4
        }
        token_list.sort(key=lambda x: priorities[x.type])
        return token_list


class Tokenifier:
    def __init__(self, tool: GalaxyToolDefinition):
        self.tool = tool    
        self.generic_scanners = [
            (scanners.get_keyval_pairs, TokenType.KV_PAIR),
            (scanners.get_quoted_numbers, TokenType.QUOTED_NUM),
            (scanners.get_quoted_strings, TokenType.QUOTED_STRING),
            (scanners.get_raw_numbers, TokenType.RAW_NUM),
            (scanners.get_raw_strings, TokenType.RAW_STRING)
        ]
        self.ordering_strategies: dict[str, TokenOrderingStrategy] = {
            'first':  FirstTokenOrderingStrategy(),
            'priority':  PriorityTokenOrderingStrategy(),
            'longest':  LongestTokenOrderingStrategy()
        }
    
    def tokenify(self, word: str, prioritisation: str='priority') -> Optional[Token]:
        """
        extracts the best token from a word.
        where multiple token types are possible, selection can be made 
        """
        token_list = self.get_all_tokens(word)
        token_list = self.perform_default_ordering(token_list)
        final_ordering = self.perform_final_ordering(token_list,  prioritisation)
        if final_ordering:
            return final_ordering[0]
        return None

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
        
        for m, var in zip(matches, base_vars):
            if var:
                if self.tool.get_input(var):
                    tokens.append(Token(m, TokenType.GX_INPUT, gxvar=var))
                elif self.tool.get_output(var):
                    tokens.append(Token(m, TokenType.GX_OUT, gxvar=var))
                else:
                    tokens.append(Token(m, TokenType.ENV_VAR))
        return tokens