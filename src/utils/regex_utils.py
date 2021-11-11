

import regex as re
import numpy as np
from typing import Optional


def get_cheetah_vars(the_string: str) -> set[str]:
    """
    doesn't keep function calls
    """
    matches = re.finditer(r'["\']?\$\{?[\w.]+\}?["\']?', the_string)
    
    #matches = set([m[0] for m in matches])
    
    keep_matches = []
    for m in matches:
        match = m[0]
        match_end = m.end()
        match = get_base_var(match)
        match = strip_method_calls(match, match_end, the_string)
        
        if match != '':
            keep_matches.append(match)

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


def get_stdout_constructs(the_string: str) -> list[str]:
    pattern = r'(?<=\s|^)(2>\&1 )?>(?=\s)|(\|&?)\stee(?=\s|$)'
    matches = re.finditer(pattern, the_string)
    return [m[0] for m in matches]


def get_words(the_string: str) -> list[str]:
    pattern = r'(\'.*?(?<!\\)\'[^\s]*)|(".*?(?<!\\)"[^\s]*)|([^\s]+)'
    matches = re.finditer(pattern, the_string)
    return [m[0] for m in matches]


def get_numbers_and_strings(the_string: str) -> list[str]:
    pattern = r'(\'.*?(?<!\\)\')|(".*?(?<!\\)")|(?<!\w)(-?\d+(\.\d+)?)(?!\d)'
    matches = re.finditer(pattern, the_string)
    return [m[0] for m in matches]


def get_quoted_numbers(the_string: str) -> list[str]:
    pattern = r'[\'"](?<!\w)(-?\d+(\.\d+)?)(?!\d)[\'"]'
    matches = re.finditer(pattern, the_string)
    matches = [m[0] for m in matches]
    return [m.strip('"\'') for m in matches]


def get_raw_numbers(the_string: str) -> list[str]:
    pattern = r'(?<=\s|^)-?\.?\d+(\.\d*)?(?=\s|$)'
    matches = re.finditer(pattern, the_string)
    return [m[0] for m in matches]


def get_quoted_strings(the_string: str) -> list[str]:
    pattern = r'(\'.*?(?<!\\)\')|(".*?(?<!\\)")'
    matches = re.finditer(pattern, the_string)
    return [m[0] for m in matches]


def get_raw_strings(the_string: str) -> list[str]:
    pattern = r'(?<=\s|^)([\/\\\w\d-.])[-\w\d\{\}\$.\/\\_:]*(?=\s|$)'
    matches = re.finditer(pattern, the_string)
    return [m[0] for m in matches]


def get_linux_operators(the_string: str) -> list[str]:
    pattern = r'^[><|]+$'
    matches = re.finditer(pattern, the_string)
    return [m[0] for m in matches]


def get_galaxy_keyword_value(the_string: str) -> Optional[str]:
    pattern = r'\\\$\{?GALAXY_.*?[\s:]-(\w+?)\}'
    matches = re.finditer(pattern, the_string)
    for m in matches:
        return m.group(1)
    return None



def get_galaxy_keywords(the_string: str) -> list[str]:
    out = []

    # handle reserved words
    gx_keywords = [
        '$__tool_directory__',
        '$__new_file_path__',
        '$__tool_data_path__',
        '$__root_dir__',
        '$__datatypes_config__',
        '$__user_id__',
        '$__user_email__',
        '$__app__',
        '$__target_datatype__',
        '\$GALAXY_MEMORY_MB',
        '\$GALAXY_MEMORY_MB_PER_SLOT',
        '\$_GALAXY_JOB_TMP_DIR'
    ]

    for reserved_word in gx_keywords:
        if reserved_word in the_string:
            out.append(reserved_word)

    # handle galaxy slots
    slots_pattern = r'\\\$\{GALAXY_SLOTS:-\d+}'
    slots_matches = re.finditer(slots_pattern, the_string)
    out += [m[0] for m in slots_matches]
    return out


def get_keyval_pairs(the_string: str) -> list[str]:
    # TODO IMPROVE
    # currently just finds key=val or key:val. will also find 'key=val' which 
    # maybe isnt good. 
    # operator_start, operator_end = find_unquoted(the_string, '=')
    
    kv_pattern = r'(?<=\s|^)\S+?[=:]\S+?(?=\s|$)'
    kv_matches = re.finditer(kv_pattern, the_string)
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
    matches = re.finditer(r'"(.*?)"|\'(.*?)\'', the_string)
    quoted_sections = [(m.start(), m.end()) for m in matches]

    # transform to mask
    quotes_mask = np.zeros(len(the_string))
    for start, end in quoted_sections:
        quotes_mask[start: end] = 1
    
    return quotes_mask