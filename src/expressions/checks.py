
import regex as re

from .patterns import (
    INTEGER,
    FLOAT,
    SIMPLE_STRINGS,
    VARIABLES_FMT1,
    VARIABLES_FMT2,
)

from .matches import get_matches


def is_int(the_string: str) -> bool:
    matches = get_matches(the_string, INTEGER)
    if matches:
        return True
    return False

def is_float(the_string: str) -> bool:
    matches = get_matches(the_string, FLOAT)
    if matches:
        return True
    return False

def is_var(the_string: str) -> bool:
    matches1 = get_matches(the_string, VARIABLES_FMT1)
    matches2 = get_matches(the_string, VARIABLES_FMT2)
    if matches1 or matches2:
        return True
    return False

def has_var(the_string: str) -> bool:
    if '$' in the_string:
        return True
    return False

def is_present(word: str, text: str) -> bool:
    pattern = rf'\s{word}\s'
    if re.findall(pattern, text):
        return True
    return False

def is_variable_substr(match: re.Match[str]) -> bool:
    """check to see if within a variable. ie file_input is within $file_input"""
    var_matches = get_matches(match.string, VARIABLES_FMT1)
    var_matches += get_matches(match.string, VARIABLES_FMT2)
    for vm in var_matches:
        if is_contained_match(match, vm):
            return True
    return False

def is_string_substr(match: re.Match[str]) -> bool:
    """check to see if delimited by \\s or / or \\ etc"""
    str_matches = get_matches(match.string, SIMPLE_STRINGS)
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

def items_are_ints(values: list[str]) -> bool:
    if not values:
        return False
    if all([is_int(val) for val in values]):
        return True
    return False

def items_are_floats(values: list[str]) -> bool:
    if not values:
        return False
    if all([is_float(val) for val in values]):
        return True
    return False

def items_are_vars(values: list[str]) -> bool:
    if not values:
        return False
    if all([is_var(val) for val in values]):
        return True
    return False