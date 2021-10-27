

# pyright: basic


from typing import Union, Tuple
import re
import xml.etree.ElementTree as et
import numpy as np


from classes.datastructures.Params import Param
from classes.datastructures.Command import Command, CommandLine
from classes.Logger import Logger

from utils.regex_utils import find_unquoted

"""
role of this module is to preprocess the command string into a useable state

aim is to remove constructs like cheetah comments, conditional lines without
removing other elements like #set directives which will be used later. 

command string is also de-indented and generally cleaned (blank lines removed etc)

returns list of CommandLines
"""


class CommandParser:
    def __init__(self, tree: et.ElementTree, logger: Logger):
        self.tree = tree
        self.logger = logger
        self.keywords = self.get_keywords()


    def get_keywords(self) -> None:
        conditional_keywords = ['#if ', '#else if ', '#elif ', '#else', '#end if', '#unless ', '#end unless']
        loop_keywords = ['#for', '#end for', '#while', '#end while']
        error_keywords = ['#try', '#except', '#end try']
        return conditional_keywords + loop_keywords + error_keywords
        

    def parse(self) -> list[str]:
        # clean the command string
        command_string = self.get_command_string()
        lines = self.split_command(command_string)
        lines = self.remove_comments(lines)
        lines = self.remove_ands(lines)
        lines = self.remove_bash_constructs(lines)
        lines = self.remove_cheetah_definitions(lines)
        lines = self.remove_cheetah_misc(lines)


        # convert each line into CommandLine and annotate with properties
        command_dict = self.init_command_lines(lines)

        # lines variable does not change! the line numbers are meaningful
        command_dict = self.annotate_conditional_lines(command_dict, lines)
        command_dict = self.annotate_loop_lines(command_dict, lines)

        # format to return
        commands = list(command_dict.values())
        commands.sort(key=lambda x: x.command_num)
        return lines, commands
 

    def get_command_string(self) -> str:
        command_string = ''
        root = self.tree.getroot()
        
        for child in root: # <command> only permitted as child of <tool>
            if child.tag == 'command':
                command_string = child.text
        
        return command_string  # type: ignore 


    def split_command(self, command_string: str) -> list[str]:
        lines = command_string.split('\n')
        lines = [ln.strip() for ln in lines]
        lines = [ln for ln in lines if ln != '']
        return lines

       
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
    

    def get_quoted_sections(self, the_string: str):
        # find the areas of the string which are quoted
        matches = re.finditer(r'"(.*?)"|\'(.*?)\'', the_string)
        quoted_sections = [(m.start(), m.end()) for m in matches]

        # transform to mask
        quotes_mask = np.zeros(len(the_string))
        for start, end in quoted_sections:
            quotes_mask[start: end] = 1
        
        return quotes_mask


    def remove_ands(self, command_list: list[str]) -> list[str]:
        """
        very basic approach. could use a quotes safe approach like for comments, but likely not needed. either way probably doesn't matter if we delete them. 
        """    
        lines = [ln.replace('&&', '') for ln in command_list]
        lines = [ln.strip(' ;') for ln in lines]
        lines = [ln for ln in lines if ln != '']
        return lines


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
        banned_firstwords = ['#import', '#from', '#break', '#continue', '#pass', '#assert']
        out = []
        
        # delete non-necessary words
        for line in command_lines:
            line = line.replace('#slurp', '')
            line = line.replace('#silent', '')
        
            # only keep lines which don't start with keywords
            if not line.split(' ')[0] in banned_firstwords:
                out.append(line)
            else:
                print()

        return out


    def init_command_lines(self, lines: list[str]) -> dict[int, CommandLine]:
        """
        inits a CommandLine for every meaningful line of the command string.
        cheetah constructs are ignored
        the CommandLines will be annotated later with the constructs they appear in 
        """
        out = {}
        command_count = 0

        for i, line in enumerate(lines):
            if not any([kw in line for kw in self.keywords]):
                out[i] = CommandLine(command_count, line)
                command_count += 1

        return out
        
        
    def annotate_conditional_lines(self, command_dict: dict[int, CommandLine], lines: list[str]) -> dict[int, CommandLine]:
        """
        '#unless EXPR' is equivalent to '#if not EXPR'
        """

        if_level = 0
        unless_level = 0

        for i, line in enumerate(lines):
            # incremet conditional depth levels
            if line.startswith('#if '):
                if_level += 1
            if line.startswith('#unless '):
                unless_level += 1

            # decrement conditional depth levels
            if '#end if' in line:
                if_level -= 1
            if '#end unless' in line:
                unless_level -= 1

            if not any([kw in line for kw in self.keywords]):
                if if_level > 0 or unless_level > 0:
                    command_dict[i].in_conditional = True
                #print(command_dict[i].in_conditional, command_dict[i].text)

        return command_dict

        

    def annotate_loop_lines(self, command_dict: dict[int, CommandLine], lines: list[str]) -> dict[int, CommandLine]:
        loop_keywords = ['#for', '#end for', '#while', '#end while']

        for_level = 0
        while_level = 0

        for i, line in enumerate(lines):
            # incremet loop depth levels
            if line.startswith('#for '):
                for_level += 1
            if line.startswith('#while '):
                while_level += 1

            # decrement loop depth levels
            if '#end for' in line:
                for_level -= 1
            if '#end while' in line:
                while_level -= 1

            if not any([kw in line for kw in self.keywords]):
                if for_level > 0 or while_level > 0:
                    command_dict[i].in_loop = True
                #print(command_dict[i].in_loop, command_dict[i].text)

        return command_dict



        






    ## unused ------------------------
    def split_by_sep(self, the_input: Union[list[str], str], sep: str) -> list[str]:
        """
        splits a list or string by sep
        if list, attempts to split each elem using the sep
        flattens the output list to 1 dimension. returns list.
        """
        out_list: list[str] = []

        # if a string
        if type(the_input) == str:
            out_list += self.split_string_clean(the_input, sep) # type: ignore

        # if a list
        if type(the_input) == list:
            for elem in the_input:
                out_list += self.split_string_clean(elem, sep)
                
        return out_list


    def split_string_clean(self, the_string: str, sep: str) -> list[str]:
        """
        splits string, then removes empty elems and elem whitespace
        """
        the_list = the_string.split(sep)
        the_list = [item.strip(' ').strip('\t') for item in the_list]
        the_list = [item for item in the_list if item != '']
        return the_list

    def is_inside_quote_pairs(self, loc: int, the_string: str) -> bool:
        print(the_string[loc - 10: loc + 10])
        
        elem_count = the_string.split("'")
        if len(elem_count) % 2 == 0:
            return True

        elem_count = the_string.split('"')
        if len(elem_count) % 2 == 0:
            return True

        return False

