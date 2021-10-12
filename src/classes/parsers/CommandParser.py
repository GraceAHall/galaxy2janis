

# pyright: basic


from typing import Union, Tuple
import re
import xml.etree.ElementTree as et
import numpy as np


from classes.datastructures.Params import Param
from classes.datastructures.Command import Command
from classes.Logger import Logger


"""
Parses the command string

cleans empty lines
removes comments
splits the command into sections

cheetah stuff:
    splits conditional blocks
    loads function definitions

rest is handled by Command() class
"""


class CommandParser:
    def __init__(self, tree: et.ElementTree, logger: Logger):
        self.tree = tree
        self.logger = logger
        self.command = Command()
        

    def parse(self) -> list[str]:
        command_string = self.get_command_string()
        command_string = 'some random text \nif asdasdasdasdas  if [ ____ ] \nthen \n    ____ \nfi asdasdasdasdassa fi '

        # swap to masking approach
        mask: dict[str, np.ndarray] = {
            'bash_conditional': np.zeros(len(command_string), dtype=np.bool), 
            'bash_loop': np.zeros(len(command_string), dtype=np.bool),
            'cheetah_conditional': np.zeros(len(command_string), dtype=np.bool),
            'cheetah_loop': np.zeros(len(command_string), dtype=np.bool),
            'cheetah_func': np.zeros(len(command_string), dtype=np.bool)    
        }

        mask = self.mask_bash_conditionals(command_string, mask)
        mask = self.mask_bash_loops(command_string, mask)
        mask = self.mask_cheetah_conditionals(command_string, mask)
        mask = self.mask_cheetah_loops(command_string, mask)
        mask = self.mask_cheetah_funcs(command_string, mask)

        commands = self.split_commands(command_string)
        commands = self.clean_commands(commands)
        return commands 


    def mask_bash_conditionals(self, command_str: str, mask: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
        open_pat = 'if'
        close_pat = 'fi'
        hits = self.find_pairs(open_pat, close_pat, command_str)
        print(command_str[hits[0][0]:hits[0][1]])
        print()

    
    def find_pairs(self, open_pat: str, close_pat: str, the_string: str) -> list[Tuple[int, int]]:
        # TODO: allow start and end of string! having issues with regex
        pattern = f'\s{open_pat}\s.*?(?=(\s{close_pat}\s))'
        
        # get all matches of pattern
        hits = [(m.start(0), m.end(0)) for m in re.finditer(pattern, the_string, flags=re.DOTALL)]
        return hits


        """
        # confirm not quoted 
        for start, end in hits:
            if not self.is_inside_quote_pairs(end, command_str):
            
                # adjust the end point
                match_end = end + 3
                while command_str[match_end] not in [' ', '\n'] and match_end < len(command_str):
                    match_end = match_end + 1

                print(command_str[start: match_end])
                mask['bash_conditional'][start: match_end] = True
                print()
        print()
        """




    def extract_bash_features(self, the_string: str) -> dict[str, list[str]]:
        features = { 'conditionals': [], 'loops': [], 'other': [] }

        bash_loop_pattern = '[\n \t(]for .*?(?= done[ \n);&])'

        conditional_hits = [(m.start(0), m.end(0)) for m in re.finditer(bash_conditional_pattern, the_string)]
        loop_hits = [(m.start(0), m.end(0)) for m in re.finditer(bash_loop_pattern, the_string)]

        for start, end in conditional_hits:
            if not self.is_inside_quote_pairs(end, the_string):
                next_char = end + 3
                while the_string[next_char] not in [' ', '\n']:
                    next_char = next_char + 1

                segment = the_string[start: next_char]
                the_string = the_string[:start] + the_string[next_char:]
                features['conditionals'].append(segment)
                print(the_string)
        
        for start, end in loop_hits:
            if not self.is_inside_quote_pairs(end, the_string):
                next_char = end + 5
                while the_string[next_char] not in [' ', '\n']:
                    next_char = next_char + 1

                segment = the_string[start: next_char]
                the_string = the_string[:start] + the_string[next_char:]
                features['loops'].append(segment)
                print(the_string)
        
        print()
 

    def get_command_string(self) -> str:
        command_string = ''
        root = self.tree.getroot()
        
        for child in root: # <command> only permitted as child of <tool>
            if child.tag == 'command':
                command_string = child.text
        
        return command_string  # type: ignore 


    def split_commands(self, command_string: str) -> list[str]:
        # get list of locations of '&&' and ';'
        # for each location, subset the command str to start at that location
        # split the subset by ' if an even number of items, it was inside single quotes. if odd, ok
        # split the subset by " if an even number of items, it was inside single quotes. if odd, ok

        commands = []
        prev_slice_loc = 0

        # find instances of '&&' or ';'
        sep_locations = self.get_sep_locations(command_string)

        # confirm each is not quoted
        for loc in sep_locations:
            if not self.is_inside_quote_pairs(loc, command_string):
                commands.append(command_string[prev_slice_loc: loc])
                prev_slice_loc = loc

        commands = [c.strip(';').strip('&') for c in commands]
        #commands = [c.strip(';').strip('&').strip('\n').strip(' ').strip('\n') for c in commands]
        return commands


    def get_sep_locations(self, the_string: str) -> list[int]:
        amp_locs = [m.start() for m in re.finditer('&&', the_string)]
        semicolon_locs = [m.start() for m in re.finditer(';', the_string)]
        all_locs = amp_locs + semicolon_locs
        all_locs.sort()
        return all_locs

        
    def is_inside_quote_pairs(self, loc: int, the_string: str) -> bool:
        print(the_string[loc - 10: loc + 10])
        
        elem_count = the_string.split("'")
        if len(elem_count) % 2 == 0:
            return True

        elem_count = the_string.split('"')
        if len(elem_count) % 2 == 0:
            return True

        return False


    def clean_command(self, the_string: str) -> list[str]:
        command_lines = the_string.split('&&')
        command_lines = self.split_by_sep(command_lines, ';')
        command_lines = self.split_by_sep(command_lines, '\n')
        command_lines = self.remove_comments(command_lines)
        return command_lines
        





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


    def remove_comments(self, command_list: list[str]) -> list[str]:
        """
        removes cheetah comments from command lines
        """
        clean_list = []
        for item in command_list:
            item = item.split('##')[0]
            if item != '':
                clean_list.append(item)
        return clean_list
    
