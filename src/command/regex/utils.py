

import regex as re
import numpy as np
from typing import Optional, Tuple

from command.regex.expressions import (
    QUOTES, 
    QUOTED_SECTIONS, 
    QUOTED_STRINGS, 
    QUOTED_NUMBERS, 
    RAW_NUMBERS, 
    RAW_STRINGS, 
    SIMPLE_STRINGS, 
    WORDS, 
    KEYVAL_PAIRS, 
    VARIABLES, 
    GX_DYNAMIC_KEYWORDS, 
    GX_STATIC_KEYWORDS, 
    SH_STATEMENT_DELIMS, 
    SH_REDIRECT, 
    SH_TEE, 
    SH_STREAM_MERGE, 
)

def get_statement_delims(the_string: str) -> list[Tuple[str, str]]:
    matches = re.finditer(SH_STATEMENT_DELIMS, the_string)
    return matches

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

def get_cheetah_vars(the_string: str) -> set[str]:
    """
    doesn't keep function calls
    """
    matches = re.finditer(VARIABLES, the_string)
    #matches = set([m[0] for m in matches])
    keep_matches = []
    for m in matches:
        match = m[0]
        match_end = m.end()
        match = get_base_var(match)
        match = strip_method_calls(match, match_end, the_string)
        match = strip_common_attributes(match, match_end, the_string)
        
        if match != '':
            keep_matches.append(match)
    
    keep_matches = [m.lstrip('$') for m in keep_matches]
    return keep_matches

def get_base_var(the_string: str) -> str:
    # this would have been nice in the regex pattern 
    # but was time consuming to develop. faster this way. 
    # remove quotes if exist
    the_string = the_string.strip('"\'')
    # remove curly braces if exist
    if the_string[1] == "{" and the_string[-1] == "}":
        the_string = the_string[0] + the_string[2:-1]
    return the_string        

def strip_method_calls(match: str, match_end: int, the_string: str) -> str:
    """
    only want cheetah variable references.  
    sometimes we see python string methods attached to a galaxy param var or cheetah functions (which have similar syntax to other vars of course). Want to remove these.
    """
    if match_end < len(the_string) and the_string[match_end] == '(':
        # object method?
        if '.' in match:
            # strip back method call
            match = match.rsplit('.', 1)[0]
        else:
            # is cheetah func call.  
            match = ''
    return match

def strip_common_attributes(match: str, match_end: int, the_string: str) -> str:
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
    if match_end < len(the_string):
        for att in gx_attributes:
            if match.endswith(att):
                # strip from the right - num of chars in the att
                match = match[:-len(att)]
                # recurse
                match = strip_common_attributes(match, match_end, the_string)
    return match

def get_redirects(the_string: str) -> list[str]:
    matches = re.finditer(SH_REDIRECT, the_string)
    return [m[0] for m in matches]

def get_tees(the_string: str) -> list[str]:
    matches = re.finditer(SH_TEE, the_string)
    return [m[0] for m in matches]

def get_stream_merges(the_string: str) -> list[str]:
    matches = re.finditer(SH_STREAM_MERGE, the_string)
    return [m[0] for m in matches]

def get_words(the_string: str) -> list[str]:
    matches = re.finditer(WORDS, the_string)
    return [m[0] for m in matches]

def get_quoted_numbers(the_string: str) -> list[str]:
    matches = re.finditer(QUOTED_NUMBERS, the_string)
    matches = [m[0] for m in matches]
    return [m.strip('"\'') for m in matches]

def get_raw_numbers(the_string: str) -> list[str]:
    matches = re.finditer(RAW_NUMBERS, the_string)
    return [m[0] for m in matches]

def get_quoted_strings(the_string: str) -> list[str]:
    matches = re.finditer(QUOTED_STRINGS, the_string)
    return [m[0] for m in matches]

def get_raw_strings(the_string: str) -> list[str]:
    matches = re.finditer(RAW_STRINGS, the_string)
    return [m[0] for m in matches]

def get_simple_strings(the_string: str) -> list[str]:
    matches = re.finditer(SIMPLE_STRINGS, the_string)
    return [m[0] for m in matches]

def get_static_keywords(the_string: str) -> list[str]:
    matches = re.finditer(GX_STATIC_KEYWORDS, the_string)
    return [m[0] for m in matches]

def get_dynamic_keywords(the_string: str) -> list[str]:
    matches = re.finditer(GX_DYNAMIC_KEYWORDS, the_string)
    return [m[0] for m in matches]

def get_dynamic_keyword_values(the_string: str) -> Optional[str]:
    matches = re.finditer(GX_DYNAMIC_KEYWORDS, the_string)
    for m in matches:
        return m.group(1)
    return None

def get_keyval_pairs(the_string: str) -> list[str]:
    # TODO IMPROVE
    # currently just finds key=val or key:val. will also find 'key=val' which maybe isnt good. 
    # operator_start, operator_end = find_unquoted(the_string, '=')
    kv_matches = re.finditer(KEYVAL_PAIRS, the_string)
    return [m[0] for m in kv_matches]

def find_unquoted(the_string: str, pattern: str) -> int:
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