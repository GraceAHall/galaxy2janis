

# pyright: basic

from typing import Union
import xml.etree.ElementTree as et

from classes.datastructures.Params import Param
from classes.Logger import Logger


class CommandParser:
    def __init__(self, tree: et.ElementTree, logger: Logger):
        self.tree = tree
        self.logger = logger
        self.aliases: dict[str, str] = {}
        

    def parse(self) -> list[str]:
        command_string = self.get_command_string()
        command_lines = self.clean_command(command_string)
        # get aliases
        self.set_aliases(command_lines)
        return command_lines #, self.aliases


    def set_aliases(self, command_lines: list[str]) -> dict[str, str]:
        """
        finds all aliases in command string. 
        aliases can arise from 
            #set directives: #set var2 = var1, #set ext = '.fastq.gz'
            function calls: #set temp = $to_string($proteins)
            symbolic links:  ln -s '$in1' '$in1_name'
            file copying: cp $var1 sample.fastq
            #for directives: #for $bed in $names.beds:
            export? export TERM=vt100 (mothur_pca)

        from the above: 
        { 
            '$var1': '$var2',
            '$proteins': '$temp',
            '$in1': '$in1_name',
            '$var1': 'sample.fastq'
        }

        can query the alias dict. ie for sample.fastq, what other aliases does it have? $var1 -> sample.fastq / $var2. list these as known aliases for the param
        """
        pass


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
    
