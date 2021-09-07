

# pyright: basic

from typing import Union
import xml.etree.ElementTree as et

from classes.datastructures.Param import Param


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


    def parse(self) -> None:
        command_string = self.get_command_string()
        command_lines = self.clean_command(command_string)
        self.link_prefixes_to_params(command_lines)
        self.remove_ui_params()
        self.resolve_multi_prefix_params()
        self.split_flag_options_params()
        print()


    def get_command_string(self) -> str:
        command_string = ''

        root = self.tree.getroot()
        
        # <command> only permitted as child of <tool>
        for child in root:
            if child.tag == 'command':
                command_string = child.text
        
        return command_string  # type: ignore 


    def clean_command(self, the_string: str) -> list[str]:
        out_tasks = []

        # initial split by bash tasks
        command_list = the_string.split('&&')
        # TODO: allow for linking variables set with cheetah functions
        # command_list = self.remove_function_defs(command_list) # important!
        command_list = self.split_by_sep(command_list, ';')
        command_list = self.split_by_sep(command_list, '\n')
        command_list = self.remove_comments(command_list) # removes comments
        command_list = self.remove_cheetah_conditionals(command_list)

        return command_list
        

    def split_by_sep(self, the_input: Union[list[str], str], sep: str) -> list[str]:
        # can handle strings or list of strings
        out_list: list[str] = []

        # if a string
        if type(the_input) == str:
            out_list += self.clean_split_string(the_input, sep) # type: ignore

        # if a list
        if type(the_input) == list:
            for elem in the_input:
                out_list += self.clean_split_string(elem, sep)
                
        return out_list


    def clean_split_string(self, the_string: str, sep: str) -> list[str]:
        the_list = the_string.split(sep)
        the_list = [item.strip(' ').strip('\t') for item in the_list]
        the_list = [item for item in the_list if item != '']
        return the_list


    def remove_comments(self, command_list: list[str]) -> list[str]:
        # removes cheetah comments from command lines
        clean_list = []
        for item in command_list:
            item = item.split('##')[0]
            if item != '':
                clean_list.append(item)
        return clean_list
    

    def remove_cheetah_conditionals(self, command_list: list[str]) -> list[str]:
        """
        cheetah follows python line syntax so #if etc directives should appear at start of line
        """
        cheetah_conditionals = ['#if', '#else', '#elif', '#end', '#while', '#return', '#import', '#def']
        out_list = []
        
        for line in command_list:
            if line.split(' ', 1)[0] in cheetah_conditionals:
                for param in self.params.values():
                    if self.find_param_in_line(param, line) != -1:
                        # param var was found in line with conditional
                        self.params[param.gx_var].appears_in_conditional = True
            else:
                out_list.append(line)

        return out_list


    
    def link_prefixes_to_params(self, command_lines: list[str]) -> None:
        """
        do I have to worry about variables in paths? probs not 

        """
        for line in command_lines:
            for param in self.params.values():
                if param.is_argument == False:
                    loc = self.find_param_in_line(param, line)
                    if loc != -1:
                        param.located_in_command = True
                        self.attempt_prefix_link(param, loc, line)     
        

    def find_param_in_line(self, param: Param, command_line: str) -> int:
        var = param.gx_var
        command_list = command_line.split(' ')
        
        for i, word in enumerate(command_list):
            if var in word:
                if self.is_cheetah_var(var, word):
                    return i
        return -1


    def attempt_prefix_link(self, param: Param, i: int, command_line: list[str]) -> None:
        command_list = command_line.split(' ')
        if self.is_cheetah_var(param.gx_var, command_list[i]):

            # add the possible prefix to resolve later
            param.prefix_collector.add(i, command_list, param.gx_var)


    def is_cheetah_var(self, var: str, command_word: str) -> bool:
        """
        $var '${var}' "${var}" all valid. 
        """

        # type 1 above
        openformat = '$'
        closeformat = '' 

        # type 2 & 3 above
        if command_word[0] in ["'", '"']:
            quote = command_word[0]
            openformat = '{}{}'.format(quote, '${')
            closeformat = '{}{}'.format('}', quote)

        varopen, varclose = command_word.split(var)
        if varopen == openformat and varclose == closeformat:
            return True

        return False


    def remove_ui_params(self) -> None:
        for param in self.params.values():
            if param.prefix == '':
                if param.appears_in_conditional and not param.located_in_command:
                    param.is_ui_param = True



    def resolve_multi_prefix_params(self) -> None:
        for param_var, param in self.params.items():
            param.resolve_multiple_prefixes()
            param.set_prefix_from_collector()
            print()


    def split_flag_options_params(self) -> None:
        for param_var, param in self.params.items():
            pass
            # is the param missing a prefix?
            # TODO this is not always the case! By coincidence
            # another flag param (not included galaxy UI) might preceed!
            # rare though. 




            # check the following about param options: 
            #   all start with '-'
            #   all only consist of single word
            
            



