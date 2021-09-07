

# pyright: basic

import xml.etree.ElementTree as et

from typing import Optional


class CommandParser:
    def __init__(self, tree: et.ElementTree):
        self.tree = tree
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
        command_string = self.clean_command(command_string)
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
        

    def split_by_sep(self, the_input, sep: str) -> list[str]:
        # can handle strings or list of strings
        out_list: list[str] = []

        # if a string
        if type(the_input) == str:
            elem = the_input
            out_list += self.clean_split_string(elem, sep)

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
            if line.lsplit(' ', 1)[0] not in cheetah_conditionals:
                out_list.append(line)

        return out_list


    



    def extract_args(self, the_list: list[str]) -> dict[str, str]:
        args = {}



        return args  # TODO fix pyright so it shuts up about partially known types