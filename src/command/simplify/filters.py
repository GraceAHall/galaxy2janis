


import re
from command.regex.utils import find_unquoted, get_unpaired_quotes_start


def translate_variable_markers(cmdstr: str) -> str:
    return cmdstr.replace("__ʕ•́ᴥ•̀ʔっ♡_", "$")

def standardise_variable_format(cmdstr: str) -> str:
    """standardises different forms of a galaxy variable ${var}, $var etc"""
    cmdlines: list[str] = split_lines(cmdstr)
    outlines: list[str] = []
    for line in cmdlines:
        line = [standardise_var(word) for word in line.split(' ')]
        outlines.append(' '.join(line))
    return join_lines(outlines)

def split_lines(cmdstr: str) -> list[str]:
    lines = cmdstr.split('\n')
    lines = [ln.strip() for ln in lines]
    lines = [ln for ln in lines if ln != '']
    return lines 

def join_lines(cmdlines: list[str]) -> str:
    return '\n'.join(cmdlines)

def standardise_var(text: str) -> str:
    """
    modifies cmd word to ensure the $var format is present, rather than ${var}
    takes a safe approach using regex and resolving all vars one by one
    """
    if text == '':
        return text
    matches = re.finditer(r'\$\{[\w.]+\}', text)
    matches = [[m[0], m.start(), m.end()] for m in matches]
    if len(matches) > 0:
        m = matches[0]
        # this is cursed but trust me it removes the curly braces for the match span
        text = text[:m[1] + 1] + text[m[1] + 2: m[2] - 1] + text[m[2]:]
        text = standardise_var(text)
    return text  

def simplify_sh_constructs(cmdstr: str) -> str:
    """
    this function standardises the different equivalent 
    forms of linux operations into a single common form
    """
    cmdstr = cmdstr.replace("&amp;", "&")
    cmdstr = cmdstr.replace("&lt;", "<")
    cmdstr = cmdstr.replace("&gt;", ">")
    cmdstr = cmdstr.replace("|&", "2>&1 |")
    cmdstr = cmdstr.replace("| tee", "|tee")
    cmdstr = cmdstr.replace("1>", ">")
    return cmdstr 

def simplify_galaxy_reserved_words(cmdstr: str) -> str:
    """modifies galaxy reserved words to relevant format. only $__tool_directory__ for now."""
    cmdstr = re.sub(r"['\"]?\$__tool_directory__['\"]?/", "", cmdstr)
    return cmdstr

def remove_cheetah_comments(cmdstr: str) -> str:
    """
    removes cheetah comments from command lines
    comments can be whole line, or part way through
    """
    cmdlines: list[str] = split_lines(cmdstr)
    outlines: list[str] = []

    for line in cmdlines:
        comment_start, _ = find_unquoted(line, '##')
        if comment_start != -1:
            # override line with comment removed
            line = line[:comment_start].strip()
        # make sure we didnt trim a full line comment and now its an empty string
        if line != '':
            outlines.append(line)
    return join_lines(outlines)




"""
---------- deprecated ----------
"""

def remove_bash_constructs(cmdstr: str) -> str:
    """
    very simple for now! just removing a line if it looks like inline bash conditional. 
    should add other bash syntax (later though)
    need to eventually handle properly - LARK?
    """
    out: list[str] = []
    for line in command_lines:
        if line.startswith('if') and 'fi' in line:
            pass
        else:
            out.append(line)
    return out

def remove_cheetah_definitions(cmdstr: str) -> str:
    """
    in future this will list the function as a definition before deleting.
    may help parse commands better.
    """
    opening_tag = '#def '
    closing_tag = '#end def'
    
    lines_to_delete: list[int] = []
    level = 0
    for i, line in enumerate(command_lines):
        # handle def level
        if level > 0:
            lines_to_delete.append(i)
        if line.startswith(opening_tag):
            level += 1
        if closing_tag in line:  # safer approach than 'line = closing_tag'
            level -= 1

    # delete all lines marked as being in defs
    for i in reversed(lines_to_delete):
        del command_lines[i]
    return command_lines

def remove_cheetah_misc(cmdstr: str) -> str:
    """
    removes misc cheetah constructs from the command lines
    """
    banned_firstwords = set(['#import', '#from', '#break', '#continue', '#pass', '#assert', '#silent'])
    command_lines = [ln.replace('#slurp ', '') for ln in command_lines] # weird one
    command_lines = [ln for ln in command_lines if not ln.split(' ')[0] in banned_firstwords]
    return command_lines

def remove_unpaired_quote_text(cmdstr: str) -> str:
    """experimental. removes lines with unpaired quotes. this will be removed later."""
    return [ln for ln in command_lines if get_unpaired_quotes_start(ln) == -1]










    
