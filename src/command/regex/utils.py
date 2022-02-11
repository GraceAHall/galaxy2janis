

import regex as re
import numpy as np
from typing import Optional, Tuple

from command.regex import scanners as scanners
from command.regex.expressions import (
    QUOTES, 
    QUOTED_SECTIONS, 
    OPERATOR
)


def is_variable_substr(match: re.Match[str]) -> bool:
    """check to see if within a variable. ie file_input is within $file_input"""
    var_matches = scanners.get_variables(match.string)
    for vm in var_matches:
        if is_contained_match(match, vm):
            return True
    return False

def is_string_substr(match: re.Match[str]) -> bool:
    """check to see if delimited by \s or / or \\ etc"""
    str_matches = scanners.get_simple_strings(match.string)
    for sm in str_matches:
        if is_contained_match(match, sm):
            return True
    return False

def is_contained_match(match1: re.Match[str], match2: re.Match[str]) -> bool:
    """checks if match1 is contained within match2"""
    if match1.start() >= match2.start() and match1.end() <= match2.end():
        if match1.end() - match1.start() < match2.end() - match2.start():
            return True
    return False

def split_variable_assignment(line: str) -> Tuple[str, str]:
    operator_start, operator_end = find_unquoted(line, OPERATOR)
    left = line[:operator_start].strip()
    right = line[operator_end:].strip()
    return left, right


def get_base_variable(match: re.Match[str]) -> Optional[str]:
    """trims function calls, attributes from variable matches"""
    text: str = match[0]
    text = strip_method_calls(text, match)
    text = strip_common_attributes(text)
    if text != '':
        return text
    return None


def strip_method_calls(text: str, match: re.Match[str]) -> str:
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


def strip_common_attributes(text: str) -> str:
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
            text = strip_common_attributes(text)
    return text


def get_unpaired_quotes_start(the_string: str) -> int:
    # find all quotes
    matches = re.finditer(QUOTES, the_string)
    quote_locations = [m.start() for m in matches]
    # find paired quotes sections
    quotes_mask = get_quoted_sections(the_string)
    # check each quote is part of quoted section
    for loc in quote_locations:
        if quotes_mask[loc] != 1:
            return loc
    return -1


def find_unquoted(the_string: str, pattern: str) -> Tuple[int, int]:
    """
    finds the pattern in string. ensures section is not quoted. 
    """
    # find quoted sections of input string
    quotes_mask = get_quoted_sections(the_string)
    
    # get pattern match locations
    matches = re.finditer(pattern, the_string)
    match_spans = [(m.start(), m.end()) for m in matches]

    # check each match to see if its in a quoted section
    if len(match_spans) > 0:
        for start, end in match_spans:
            if sum(quotes_mask[start: end]) == 0:
                # return position of first unquoted match
                return start, end
    return -1, -1


def get_quoted_sections(the_string: str):
    # find the areas of the string which are quoted
    matches = re.finditer(QUOTED_SECTIONS, the_string)
    quoted_sections = [(m.start(), m.end()) for m in matches]

    # transform to mask
    quotes_mask = np.zeros(len(the_string))
    for start, end in quoted_sections:
        quotes_mask[start: end] = 1
    
    return quotes_mask