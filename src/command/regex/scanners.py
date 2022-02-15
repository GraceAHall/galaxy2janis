


import regex as re

from command.regex.expressions import (
    QUOTED_STRINGS, 
    QUOTED_NUMBERS, 
    RAW_NUMBERS, 
    RAW_STRINGS, 
    SIMPLE_STRINGS, 
    WORDS, 
    KEYVAL_PAIRS, 
    GX_DYNAMIC_KEYWORDS, 
    GX_STATIC_KEYWORDS, 
    SH_REDIRECT, 
    SH_TEE, 
    SH_STREAM_MERGE, 
    VARIABLES,
    SH_STATEMENT_DELIMS,
    ALL
)

def get_all(the_string: str) -> list[re.Match[str]]:
    matches = re.finditer(ALL, the_string)
    return [m for m in matches]

def get_custom(pattern: str, the_string: str) -> list[re.Match[str]]:
    matches = re.finditer(pattern, the_string)
    return [m for m in matches]

def get_statement_delims(the_string: str) -> list[re.Match[str]]:
    matches = re.finditer(SH_STATEMENT_DELIMS, the_string)
    return [m for m in matches]

def get_keyval_pairs(the_string: str) -> list[re.Match[str]]:
    # TODO IMPROVE
    # currently just finds key=val or key:val. will also find 'key=val' which maybe isnt good. 
    # operator_start, operator_end = find_unquoted(the_string, '=')
    kv_matches = re.finditer(KEYVAL_PAIRS, the_string)
    return [m for m in kv_matches]

def get_variables(the_string: str) -> list[re.Match[str]]:
    matches = re.finditer(VARIABLES, the_string)
    return [m for m in matches]

def get_redirects(the_string: str) -> list[re.Match[str]]:
    matches = re.finditer(SH_REDIRECT, the_string)
    return [m for m in matches]

def get_tees(the_string: str) -> list[re.Match[str]]:
    matches = re.finditer(SH_TEE, the_string)
    return [m for m in matches]

def get_stream_merges(the_string: str) -> list[re.Match[str]]:
    matches = re.finditer(SH_STREAM_MERGE, the_string)
    return [m for m in matches]

def get_words(the_string: str) -> list[re.Match[str]]:
    matches = re.finditer(WORDS, the_string)
    return [m for m in matches]

def get_quoted_numbers(the_string: str) -> list[re.Match[str]]:
    matches = re.finditer(QUOTED_NUMBERS, the_string)
    matches = [m for m in matches]
    return [m.strip('"\'') for m in matches]

def get_raw_numbers(the_string: str) -> list[re.Match[str]]:
    matches = re.finditer(RAW_NUMBERS, the_string)
    return [m for m in matches]

def get_quoted_strings(the_string: str) -> list[re.Match[str]]:
    matches = re.finditer(QUOTED_STRINGS, the_string)
    return [m for m in matches]

def get_raw_strings(the_string: str) -> list[re.Match[str]]:
    matches = re.finditer(RAW_STRINGS, the_string)
    return [m for m in matches]

def get_simple_strings(the_string: str) -> list[re.Match[str]]:
    matches = re.finditer(SIMPLE_STRINGS, the_string)
    return [m for m in matches]

def get_static_keywords(the_string: str) -> list[re.Match[str]]:
    matches = re.finditer(GX_STATIC_KEYWORDS, the_string)
    return [m for m in matches]

def get_dynamic_keywords(the_string: str) -> list[re.Match[str]]:
    matches = re.finditer(GX_DYNAMIC_KEYWORDS, the_string)
    return [m for m in matches]

