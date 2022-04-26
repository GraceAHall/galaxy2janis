


import regex as re

from command.regex.expressions import (
    VARIABLES_FMT1,
    VARIABLES_FMT2,
    FUNCTION_CALL_FMT1,
    FUNCTION_CALL_FMT2,
    QUOTED_STRINGS, 
    QUOTED_NUMBERS, 
    BACKTICK_SECTIONS,
    QUOTED_SECTIONS,
    QUOTED_SECTION_W_NEWLINE,
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
    SH_STATEMENT_DELIMS,
    VERSIONS,
    COMPOUND_OPT,
    ALL
)


def get_all(the_string: str) -> list[re.Match[str]]:
    matches = re.finditer(ALL, the_string)
    return [m for m in matches]

def get_compound_opt(the_string: str) -> list[re.Match[str]]:
    matches = re.finditer(COMPOUND_OPT, the_string)
    return [m for m in matches]

def get_preceeding_dashes(search_term: str, text: str) -> list[str]:
    PRECEEDING_DASHES = r'(?<![$.{])(-+?)' + fr'({search_term})' + r'(?=[\s=:]|$|[\'"])'
    matches = re.finditer(PRECEEDING_DASHES, text)
    return [m.group(1) for m in matches]

def get_backtick_sections(the_string: str) -> list[re.Match[str]]:
    matches = re.finditer(BACKTICK_SECTIONS, the_string)
    return [m for m in matches]

def get_quoted_sections(the_string: str) -> list[re.Match[str]]:
    matches = re.finditer(QUOTED_SECTIONS, the_string)
    return [m for m in matches]

def get_quoted_sections_w_newline(the_string: str) -> list[re.Match[str]]:
    matches = re.finditer(QUOTED_SECTION_W_NEWLINE, the_string)
    return [m for m in matches]

def get_custom(pattern: str, the_string: str) -> list[re.Match[str]]:
    matches = re.finditer(pattern, the_string)
    return [m for m in matches]

def get_versions(the_string: str) -> list[re.Match[str]]:
    matches = re.finditer(VERSIONS, the_string)
    return [m for m in matches]

def get_statement_delims(the_string: str) -> list[re.Match[str]]:
    matches = re.finditer(SH_STATEMENT_DELIMS, the_string)
    return [m for m in matches]

def get_keyval_pairs(the_string: str) -> list[re.Match[str]]:
    # TODO IMPROVE
    # currently just finds key=val or key:val. will also find 'key=val' which maybe isnt good. 
    # operator_start, operator_end = find_unquoted(the_string, '=')
    kv_matches = re.finditer(KEYVAL_PAIRS, the_string)
    # find whether there is an '=' in the_string
    # split the_string using this delim
    # identify whether there are 2 units either side. 
    return [m for m in kv_matches]

def get_variables_fmt1(the_string: str) -> list[re.Match[str]]:
    matches = re.finditer(VARIABLES_FMT1, the_string)
    return [m for m in matches]

def get_variables_fmt2(the_string: str) -> list[re.Match[str]]:
    matches = re.finditer(VARIABLES_FMT2, the_string)
    return [m for m in matches]

def get_function_calls(the_string: str) -> list[re.Match[str]]:
    matches = [m for m in re.finditer(FUNCTION_CALL_FMT1, the_string)]
    matches += [m for m in re.finditer(FUNCTION_CALL_FMT2, the_string)]
    return matches

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

