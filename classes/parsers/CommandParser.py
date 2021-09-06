

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
        tasks = the_string.split('&&')
        #tasks = self.split_by_sep(tasks, ';')

        for task in tasks:
            # third split by newlines
            the_list = self.split_by_sep(task, '\n')
            #the_list = self.split_by_sep(task, '\n')

            # handle cheetah variable setting and logic
            the_list = self.handle_cheetah(the_list)

            # exclude tasks if they begin with banned linux terms?
            
            out_tasks.append(the_list)
            print()
        
        # extract args
        #the_list = self.extract_args(the_list)
        
        return out_tasks
        

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


    def handle_cheetah(self, the_list: list[str]) -> list[str]:
        """
        need to handle:
            ## (comments) 
            #set
            #if
            #else
            #elif
            #end if
        """
        the_list = self.clean_comments(the_list)
        return the_list


    def clean_comments(self, the_list: list[str]) -> list[str]:
        # removes cheetah comments from command lines
        clean_list = []
        for item in the_list:
            item = item.split('##')[0]
            if item != '':
                clean_list.append(item)
        return clean_list



    def extract_args(self, the_list: list[str]) -> dict[str, str]:
        args = {}



        return args  # TODO fix pyright so it shuts up about partially known types