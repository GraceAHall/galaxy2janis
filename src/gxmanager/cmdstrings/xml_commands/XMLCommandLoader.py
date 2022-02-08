

# pyright: basic

import regex as re

from command.expressions.regex_utils import find_unquoted, get_unpaired_quotes_start
from tool.tool_definition import GalaxyToolDefinition


class XMLCommandLoader:
    """
    loads and processes xml command section
    the raw xml command string is processed into a more usable state
    aim is to remove constructs like cheetah comments, conditional lines without
    removing other elements like #set directives which will be used later. 

    some stdio stuff is managed here. '| tee ', '|& tee ', 2>&1 etc are found and replaced or just removed for better understanding. 
    command string is also de-indented and generally cleaned (blank lines removed etc)
    process
    """
    def __init__(self, tooldef: GalaxyToolDefinition):
        self.tooldef = tooldef

    def load(self) -> list[str]:
        command_string = self.get_command_string()
        command_lines = self.get_command_lines(command_string)
        return command_lines

    def get_command_string(self) -> str:
        command_string = self.simplify_stdio(self.tooldef.command)
        return self.simplify_galaxy_reserved_words(command_string)
        
    def simplify_stdio(self, command_string: str) -> str:
        """
        this function aims to remove some of the more complex constructs in the tool xml command
        """
        command_string = command_string.replace("&amp;", "&")
        command_string = command_string.replace(">>", ">")
        command_string = command_string.replace("| tee ", "> ")
        command_string = command_string.replace("| tee\n", "> ")
        command_string = command_string.replace("|& tee ", "> ")
        command_string = command_string.replace("|& tee\n", "> ")
        command_string = command_string.replace("2>&1", "")
        command_string = command_string.replace("1>&2", "")
        command_string = command_string.replace(">&2", "")
        command_string = re.sub(r'2> \S+', '', command_string)
        return command_string 

    def simplify_galaxy_reserved_words(self, command_string: str) -> str:
        """modifies galaxy reserved words to relevant format. only $__tool_directory__ for now."""
        command_string = re.sub(r"['\"]?\$__tool_directory__['\"]?/", "", command_string)
        return command_string

    def get_command_lines(self, command_string: str) -> list[str]:
        lines = self.split_lines(command_string)
        lines = self.standardise_variable_format(lines)
        lines = self.remove_comments(lines)
        lines = self.remove_bash_constructs(lines)
        lines = self.remove_cheetah_definitions(lines)
        lines = self.remove_cheetah_misc(lines)
        # NOTE experimental
        lines = self.remove_unpaired_quote_text(lines)
        return lines

    def split_lines(self, command_string: str) -> list[str]:
        lines = command_string.split('\n')
        lines = [ln.strip() for ln in lines]
        lines = [ln for ln in lines if ln != '']
        return lines
    
    def standardise_variable_format(self, cmd_lines: list[str]) -> list[str]:
        out_lines: list[str] = []

        for line in cmd_lines:
            line = line.split(' ')
            linewords: list[str] = []
            for word in line:
                word = self.standardise_var(word)
                linewords.append(word)

            linestr = ' '.join(linewords)
            out_lines.append(linestr)
        return out_lines

    def standardise_var(self, text: str) -> str:
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
            text = self.standardise_var(text)
        return text  
       
    def remove_comments(self, command_list: list[str]) -> list[str]:
        """
        removes cheetah comments from command lines
        comments can be whole line, or part way through
        """
        clean_list: list[str] = []
        for line in command_list:
            comment_start, _ = find_unquoted(line, '##')
            if comment_start != -1:
                # override line with comment removed
                line = line[:comment_start].strip()
            # make sure we didnt trim a full line comment and now its an empty string
            if line != '':
                clean_list.append(line)
        return clean_list

    def remove_bash_constructs(self, command_lines: list[str]) -> list[str]:
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

    def remove_cheetah_definitions(self, command_lines: list[str]) -> list[str]:
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

    def remove_cheetah_misc(self, command_lines: list[str]) -> list[str]:
        """
        removes misc cheetah constructs from the command lines
        """
        banned_firstwords = set(['#import', '#from', '#break', '#continue', '#pass', '#assert', '#silent'])
        command_lines = [ln.replace('#slurp ', '') for ln in command_lines] # weird one
        command_lines = [ln for ln in command_lines if not ln.split(' ')[0] in banned_firstwords]
        return command_lines

    def remove_unpaired_quote_text(self, command_lines: list[str]) -> list[str]:
        """removes lines with unpaired quotes. this will be removed later."""
        return [ln for ln in command_lines if get_unpaired_quotes_start(ln) == -1]

    
    
    