

import re
import numpy as np



def get_numbers_and_strings(the_string: str):
    pattern = r'(".*?(?<!\\)")|(\'.*?(?<!\\)\')|(?<!\w)(-?\d+(\.\d+)?)(?!\d)'
    matches = re.finditer(pattern, the_string)
    return [m[0] for m in matches]


def extract_cheetah_vars(the_string: str) -> set[str]:
    """
    doesn't keep function calls
    """
    matches = re.finditer(r'["\']?\$\{?[\w.]+\}?["\']?', the_string)
    
    #matches = set([m[0] for m in matches])
    
    keep_matches = []
    for m in matches:
        # check if there is a '(' in the string
        if m.end() < len(the_string) and the_string[m.end()] == '(':
            # is an object method being called?
            if '.' in m[0]:
                # strip back method call
                adjusted_match = m[0].rsplit('.', 1)[0]
                keep_matches.append(adjusted_match)
            else:
                # is cheetah func call. ignore match. 
                continue
        else:
            keep_matches.append(m[0])

    return keep_matches



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