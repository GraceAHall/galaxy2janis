

# pyright: basic

from typing import Union
import xml.etree.ElementTree as et

from classes.datastructures.Params import Param


class CommandParser:
    def __init__(self, tree: et.ElementTree, params: dict[str, Param]):
        self.tree = tree
        self.params = params
        self.banned_commands = [
            'cp', 'tar', 'mkdir', 'pwd',
            'which', 'cd', 'ls', 'cat', 'mv',
            'rmdir', 'rm', 'touch', 'locate', 'find',
            'grep', 'head', 'tail', 'chmod', 'chown', 
            'wget', 'echo', 'zip', 'unzip', 'gzip',
            'gunzip', 'export'
        ]


    def parse(self) -> list[str]:
        command_string = self.get_command_string()
        command_lines = self.clean_command(command_string)
        print()
        #self.link_prefixes_to_params(command_lines)
        #self.mark_ui_params()
        #self.resolve_multi_prefix_params()
        return command_lines


    def get_command_string(self) -> str:
        command_string = ''

        root = self.tree.getroot()
        
        # <command> only permitted as child of <tool>
        for child in root:
            if child.tag == 'command':
                command_string = child.text
        
        return command_string  # type: ignore 


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
    

    # Param()
    def remove_cheetah_conditionals(self, command_list: list[str]) -> list[str]:
        """
        removes conditional logic from command. marks variables which appear in conditional logic (as may be solely UI params)
        """
        cheetah_conditionals = ['#if', '#else', '#elif', '#end', '#while', '#return', '#import', '#def']
        out_list = []
        
        for line in command_list:
            if line.split(' ', 1)[0] in cheetah_conditionals:
                for param in self.params.values():
                    if self.find_param_in_line(param, line) != -1:
                        # mark param as found in line with conditional
                        self.params[param.gx_var].appears_in_conditional = True
            else:
                out_list.append(line)

        return out_list


    # Param()
    def link_prefixes_to_params(self, command_lines: list[str]) -> None:
        """
        after param is found in command string, looks at prev word to identify 
        whether it looks like a prefix
        """
        for line in command_lines:
            for param in self.params.values():
                if param.is_argument == False:
                    loc = self.find_param_in_line(param, line)
                    if loc != -1:
                        param.located_in_command = True
                        self.attempt_prefix_link(param, loc, line)     
        

    # Param()
    def find_param_in_line(self, param: Param, command_line: str) -> int:
        var = param.gx_var
        command_list = command_line.split(' ')
        
        for i, word in enumerate(command_list):
            if var in word:
                if self.confirm_cheetah_var(var, word):
                    return i

        return -1


    # Param()
    def confirm_cheetah_var(self, var: str, command_word: str) -> bool:
        """
        $var '${var}' "${var}" '$var' "$var" all valid. 
        """

        # sometimes its last word in conditional logic line
        command_word = command_word.rstrip(':')

        # confirm quote pairs
        if command_word[0] in ['"', "'"]:
            if command_word[-1] != command_word[0]:
                return False
        command_word = command_word.strip('"').strip("'")

        # confirm $ beginning
        # possible values at this stage: [$var, ${var}]
        if command_word[0] != '$':
            return False
        command_word = command_word.strip('$')
        
        # handle curly brackets
        # possible values at this stage: [var, {var}]
        if command_word[0] == '{':
            if command_word[-1] != '}':
                return False
        command_word = command_word.strip('{').strip('}')

        # command_word should now equal var
        if command_word != var:
            return False
        
        return True


    # Param()
    def attempt_prefix_link(self, param: Param, i: int, command_line: list[str]) -> None:
        command_list = command_line.split(' ')
        if self.confirm_cheetah_var(param.gx_var, command_list[i]):
            param.prefix_collector.add(i, command_list, param.gx_var)

    # Param()
    def mark_ui_params(self) -> None:
        for param in self.params.values():
            if param.prefix == '':
                if param.appears_in_conditional and not param.located_in_command:
                    param.is_ui_param = True

    # Param()
    def resolve_multi_prefix_params(self) -> None:
        """
        Just in case we find two possible valid prefixes for a param
        """
        for param in self.params.values():
            param.resolve_multiple_prefixes()
            param.set_prefix_from_collector()
            print()

            



