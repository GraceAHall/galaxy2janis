

import regex as re

from abc import ABC, abstractmethod
from typing import Optional

from gx.gxtool.XMLToolDefinition import XMLToolDefinition
from .Token import Token, TokenType
from . import utils as token_utils

import expressions
from expressions.patterns import (
    QUOTED_NUMBERS,
    QUOTED_STRINGS,
    RAW_NUMBERS,
    RAW_STRINGS,
    SH_REDIRECT,
    SH_TEE,
    SH_STREAM_MERGE,
    GX_DYNAMIC_KEYWORDS,
    GX_STATIC_KEYWORDS,
    EMPTY_STRINGS,
    VARIABLES_FMT1,
    VARIABLES_FMT2,
    ALL,
)


def strip_to_base_variable(match: re.Match[str]) -> Optional[str]:
    """trims function calls, attributes from variable matches"""
    text: str = match[0]
    text = _strip_quotes(text)
    text = _strip_braces(text)
    text = _strip_method_calls(text, match)
    text = _strip_common_attributes(text)
    if text != '':
        return text
    return None

def _strip_quotes(text: str) -> str:
    text = text.replace('"', '')
    text = text.replace("'", '')
    return text

def _strip_braces(text: str) -> str:
    if text[1] == '{':
        text = text[0] + text[2:]
    if text[-1] == '}':
        text = text[:-1]
    # text = text.replace('{', '')
    # text = text.replace('}', '')
    return text

def _strip_method_calls(text: str, match: re.Match[str]) -> str:
    """
    only want cheetah variable references.  
    sometimes we see python string methods attached to a galaxy param var or cheetah functions (which have similar syntax to other vars of course). Want to remove these.
    """
    if match.end() < len(match.string) and match.string[match.end()] == '(':
        # object method?
        if '.' in text:
            # strip back method call
            text = text.rsplit('.', 1)[0]
        else:
            # is cheetah func call.  
            text = ''
    return text

def _strip_common_attributes(text: str) -> str:
    return text
    gx_attributes = set([
        '.forward',
        '.reverse',
        '.ext',
        '.value',
        '.name',
        '.files_path',
        '.element_identifier'
    ])
    # needs to be recursive so we can iterately peel back 
    # eg  in1.forward.ext
    # need to peel .ext then peel .forward.
    for att in gx_attributes:
        if text.endswith(att):
            # strip from the right - num of chars in the att
            text = text[:-len(att)]
            # recurse
            text = _strip_common_attributes(text)
    return text





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
            TokenType.FUNCTION_CALL: 0,
            TokenType.BACKTICK_SHELL_STATEMENT: 0,
            TokenType.GX_KW_DYNAMIC: 1,
            TokenType.GX_KW_STATIC: 2,
            TokenType.KV_PAIR: 3,
            TokenType.KV_LINKER: 3,
            TokenType.GX_INPUT: 4,
            TokenType.GX_OUTPUT: 4,
            TokenType.ENV_VAR: 5,
            TokenType.QUOTED_NUM: 6,
            TokenType.QUOTED_STRING: 7,
            TokenType.RAW_STRING: 8,
            TokenType.RAW_NUM: 9,
            TokenType.LINUX_TEE: 10,
            TokenType.LINUX_REDIRECT: 10,
            TokenType.LINUX_STREAM_MERGE: 10,
            TokenType.EMPTY_STRING: 11,
            TokenType.UNKNOWN: 999,
        }
        token_list.sort(key=lambda x: priorities[x.type])
        return token_list


class TokenFactory:
    def __init__(self, xmltool: Optional[XMLToolDefinition]=None):
        self.xmltool = xmltool
        self.generic_scanners = [
            (QUOTED_NUMBERS, TokenType.QUOTED_NUM),
            (QUOTED_STRINGS, TokenType.QUOTED_STRING),
            (RAW_NUMBERS, TokenType.RAW_NUM),
            (RAW_STRINGS, TokenType.RAW_STRING),
            (SH_REDIRECT, TokenType.LINUX_REDIRECT),
            (SH_TEE, TokenType.LINUX_TEE),
            (SH_STREAM_MERGE, TokenType.LINUX_STREAM_MERGE),
            (GX_DYNAMIC_KEYWORDS, TokenType.GX_KW_DYNAMIC),
            (GX_STATIC_KEYWORDS, TokenType.GX_KW_STATIC),
            (EMPTY_STRINGS, TokenType.EMPTY_STRING),
            (ALL, TokenType.UNKNOWN)
        ]
        self.ordering_strategies: dict[str, TokenOrderingStrategy] = {
            'first':  FirstTokenOrderingStrategy(),
            'priority':  PriorityTokenOrderingStrategy(),
            'longest':  LongestTokenOrderingStrategy()
        }

    def create(self, word: str, prioritisation: str='priority') -> list[Token]:
        kv_split_tokens = self.create_kv_tokens(word, prioritisation)
        if kv_split_tokens:
            return kv_split_tokens
        else:
            token = self.create_single(word, prioritisation)
            return [token]

    def create_kv_tokens(self, word: str, prioritisation: str='priority') -> list[Token]:
        left_token_allowed_types = [
            TokenType.RAW_STRING,
            TokenType.RAW_NUM,
        ]
        right_token_allowed_types = [
            TokenType.RAW_STRING,
            TokenType.RAW_NUM,
            TokenType.QUOTED_STRING,
            TokenType.QUOTED_NUM,
            TokenType.GX_INPUT,
            TokenType.GX_OUTPUT,
            TokenType.GX_KW_DYNAMIC,
            TokenType.GX_KW_STATIC,
            TokenType.ENV_VAR
        ]
        delims = ['=', ':']
        for delim in delims:
            if delim in word:
                left, right = word.split(delim, 1)
                left_token = self.create_single(left, prioritisation)
                right_token = self.create_single(right, prioritisation)
                if left_token.type in left_token_allowed_types:
                    if right_token.type in right_token_allowed_types:
                        return [left_token, token_utils.spawn_kv_linker(delim), right_token]
        return []

    def create_single(self, word: str, prioritisation: str='priority') -> Token:
        """
        extracts the best token from a word.
        where multiple token types are possible, selection can be made 
        """
        token_list = self.get_all_tokens(word)
        token_list = self.perform_default_ordering(token_list)
        final_ordering = self.perform_final_ordering(token_list, prioritisation)
        final_token = self.select_final_token(final_ordering)
        return final_token

    def select_final_token(self, ordered_token_list: list[Token]) -> Token:
        # a few overrides to ensure things make sense 
        
        # full length string (helps for )
        # if self.has_full_length_quoted_token(ordered_token_list):
        #     if not self.has_semi_full_length_var_match(ordered_token_list):
       
        # normal approach (priority based)
        final_token = ordered_token_list[0]
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
        tokens += self.get_dunder_token(the_string)
        tokens += self.get_generic_tokens(the_string)
        tokens += self.get_variable_tokens(the_string)
        return tokens

    def get_dunder_token(self, the_string: str) -> list[Token]:
        if the_string == '__FUNCTION_CALL__':
            return [token_utils.spawn_function_call()]
        if the_string == '__BACKTICK_SHELL_STATEMENT__':
            return [token_utils.spawn_backtick_section()]
        return []

    def get_generic_tokens(self, the_string: str) -> list[Token]:
        """gets all tokens except galaxy/env variables"""
        tokens: list[Token] = []
        for pattern, ttype in self.generic_scanners:
            matches = expressions.get_matches(the_string, pattern)
            tokens += [Token(m, ttype) for m in matches]
        return tokens

    def get_variable_tokens(self, the_string: str) -> list[Token]:
        """gets tokens for galaxy/env variables"""
        tokens: list[Token] = []
        matches = expressions.get_matches(the_string, VARIABLES_FMT1)
        matches += expressions.get_matches(the_string, VARIABLES_FMT2)
        base_vars = [strip_to_base_variable(m) for m in matches]
        
        for m, varname in zip(matches, base_vars):
            if varname and self.xmltool:
                if self.xmltool.get_input(varname):
                    tokens.append(Token(m, TokenType.GX_INPUT, gxparam=self.xmltool.get_input(varname)))
                elif self.xmltool.get_output(varname):
                    tokens.append(Token(m, TokenType.GX_OUTPUT, gxparam=self.xmltool.get_output(varname)))
                else:
                    tokens.append(Token(m, TokenType.ENV_VAR))
        return tokens
    
    