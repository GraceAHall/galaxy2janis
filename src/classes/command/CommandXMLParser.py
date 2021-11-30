

# pyright: basic

import xml.etree.ElementTree as et
import regex as re
from collections import defaultdict

from classes.command.AliasExtractor import AliasExtractor
from classes.command.CommandBlock import CommandBlock
from classes.params.ParamRegister import ParamRegister
from classes.outputs.OutputRegister import OutputRegister
from classes.logging.Logger import Logger

from utils.token_utils import split_line_by_ands
from utils.regex_utils import (
    find_unquoted, 
    get_unpaired_quotes_start, 
    get_words, 
    get_galaxy_keywords, 
    get_galaxy_keyword_value
)


# class CommandWord:
#     def __init__(self, text: str, statement_block: int):
#         self.text = text
#         self.statement_block = statement_block
#         self.in_loop = False
#         self.in_conditional = False
#         self.expanded_text: list[str] = []



class CommandXMLParser:
    """
    role of this module is to preprocess the command string into a useable state

    aim is to remove constructs like cheetah comments, conditional lines without
    removing other elements like #set directives which will be used later. 

    some stdio stuff is managed here. '| tee ', '|& tee ', 2>&1 etc are found and replaced or just removed for better understanding. 

    command string is also de-indented and generally cleaned (blank lines removed etc)


    process
    - loads command from XMl
    - cleans lines


    """
    def __init__(self, command_section: str, logger: Logger):
        self.command_section = command_section
        self.logger = logger
        self.command_string = self.get_command_string()
        self.command_lines = self.get_command_lines()
        
       
    def get_command_string(self) -> str:
        command_string = self.simplify_stdio(self.command_section)
        return self.simplify_galaxy_reserved_words(command_string)
        

    def get_command_from_xmltree(self) -> str:
        command_string = ''
        root = self.tree.getroot()
        
        for child in root: # <command> only permitted as child of <tool>
            if child.tag == 'command':
                command_string = child.text
        
        return command_string  # type: ignore


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
        command_string = re.sub('2> \S+', '', command_string)
        return command_string 


    def simplify_galaxy_reserved_words(self, command_string: str) -> str:
        command_string = re.sub("['\"]?\$__tool_directory__['\"]?/", "", command_string)
        return command_string


    def get_command_lines(self) -> list[str]:
        lines = self.split_lines(self.command_string)
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

    
    def standardise_variable_format(self, cmd_lines: list[str]) -> str:
        out_lines = []

        for line in cmd_lines:
            line = line.split(' ')
            out_line = []
            for word in line:
                word = self.standardise_var(word)
                out_line.append(word)

            out_line = ' '.join(out_line)
            out_lines.append(out_line)
        return out_lines


    def standardise_var(self, text: str) -> str:
        """
        modifies cmd word to ensure the $var format is present, 
        rather than ${var}
        takes a safe approach using regex and resolving all vars one by one
        """
        if text == '':
            return text

        matches = re.finditer(r'\$\{[\w.]+\}', text)
        matches = [[m[0], m.start(), m.end()] for m in matches]

        if len(matches) > 0:
            m = matches[0]
            # this is cursed but trust me it removes the 
            # curly braces for the match span
            text = text[:m[1] + 1] + text[m[1] + 2: m[2] - 1] + text[m[2]:]
            text = self.standardise_var(text)

        return text  

       
    def remove_comments(self, command_list: list[str]) -> list[str]:
        """
        removes cheetah comments from command lines
        comments can be whole line, or part way through
        """
        clean_list = []

        for line in command_list:
            comment_start, comment_end = find_unquoted(line, '##')
            if comment_start != -1:
                # override line with comment removed
                line = line[:comment_start]
                line = line.strip()
            
            # make sure we didnt trim a full line comment 
            # and now its an empty string
            if line != '':
                clean_list.append(line)

        return clean_list


    def remove_bash_constructs(self, command_lines: list[str]) -> list[str]:
        """
        very simple for now! just removing a line if it looks like inline bash conditional. 
        should add other bash syntax (later though)

        need to eventually handle properly - LARK?
        """
        out = []
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
        
        lines_to_delete = []
        level = 0

        for i, line in enumerate(command_lines):
            # handle def level
            if line.startswith(opening_tag):
                level += 1
            if closing_tag in line:  # safer approach than 'line = closing_tag'
                lines_to_delete.append(i) # dont forget '#end def' line
                level -= 1

            if level > 0:
                lines_to_delete.append(i)

        # delete all lines marked as being in defs
        for i in reversed(lines_to_delete):
            del command_lines[i]
        
        return command_lines


    def remove_cheetah_misc(self, command_lines: list[str]) -> list[str]:
        """
        yea yea
        """
        banned_firstwords = ['#import', '#from', '#break', '#continue', '#pass', '#assert', '#silent']
        out_lines = []
        
        # delete non-necessary words
        for line in command_lines:
            line = line.replace('#slurp ', '')
        
            # only keep lines which don't start with keywords
            if not line.split(' ')[0] in banned_firstwords:
                out_lines.append(line)

        return out_lines


    def remove_unpaired_quote_text(self, command_lines: list[str]) -> list[str]:
        out_lines = []
        for line in command_lines:
            unpaired_quotes_start = get_unpaired_quotes_start(line)
            
            # keep line if no unpaired quotes else continue
            if unpaired_quotes_start != -1:
                continue
            else:
                out_lines.append(line)
        
        return out_lines

    
    
    