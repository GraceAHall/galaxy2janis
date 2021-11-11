

# pyright: basic


from typing import Union
import xml.etree.ElementTree as et
from classes.command.Command import Command

from classes.command.CommandProcessor import CommandWord
from classes.Logger import Logger

from utils.regex_utils import find_unquoted, get_words, get_galaxy_keyword_value

"""
role of this module is to preprocess the command string into a useable state

aim is to remove constructs like cheetah comments, conditional lines without
removing other elements like #set directives which will be used later. 

some stdio stuff is managed here. '| tee ', '|& tee ', 2>&1 etc are found and replaced or just removed for better understanding. 

command string is also de-indented and generally cleaned (blank lines removed etc)

returns list of CommandWords
after this module, the list of CommandWord() gets parsed to CommandProcessor() which processes the words into an actual Command()

"""


class CommandParser:
    def __init__(self, tree: et.ElementTree, logger: Logger):
        self.tree = tree
        self.logger = logger
        self.keywords = self.get_keywords()


    def get_keywords(self) -> None:
        conditional_keywords = ['#if ', '#else if ', '#elif ', '#else', '#end if', '#unless ', '#end unless']
        loop_keywords = ['#for ', '#end for', '#while ', '#end while']
        error_keywords = ['#try ', '#except', '#end try']
        cheetah_var_keywords = ['#def ', '#set ']
        linux_commands = ['set ', 'ln ', 'cp ', 'mkdir ', 'tar ', 'ls ', 'head ', 'wget ', 'grep ', 'awk ', 'cut ', 'sed ', 'export ', 'gzip ', 'gunzip ']
        return conditional_keywords + loop_keywords + error_keywords + cheetah_var_keywords + linux_commands
        

    def parse(self) -> list[str]:
        # clean the command string
        command_string = self.get_command_string()
        command_string = self.simplify_stdio(command_string)
        lines = self.split_command(command_string)
        lines = self.remove_comments(lines)
        lines = self.remove_ands(lines)
        lines = self.remove_bash_constructs(lines)
        lines = self.remove_cheetah_definitions(lines)
        lines = self.remove_cheetah_misc(lines)
        # lines variable does not change from here! the line numbers are meaningful

        # convert each line into CommandWord and annotate with properties
        command_dict = self.init_command_words(lines)
        command_dict = self.annotate_conditional_words(command_dict, lines)
        command_dict = self.annotate_loop_words(command_dict, lines)

        # remove everything 
        command_words = self.convert_to_words(command_dict)
        command_words = self.translate_gx_keywords(command_words)
        command_words = self.truncate_extra_commands(command_words)

        # post sentinel & return
        command_words.append(CommandWord('__END_COMMAND__'))
        return lines, command_words
 

    def get_command_string(self) -> str:
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

        return command_string


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
            line = line.replace('#slurp ', '')
            line = line.replace('#silent ', '')
        
            # only keep lines which don't start with keywords
            if not line.split(' ')[0] in banned_firstwords:
                out.append(line)
            else:
                print()

        return out


    def init_command_words(self, lines: list[str]) -> dict[int, list[CommandWord]]:
        """
        inits a CommandWord for every meaningful line of the command string.
        keys in the dict are line numbers, vals are list of CommandWord

        cheetah constructs are ignored

        the CommandWords will be annotated later with the constructs they appear in 
        """
        command_words = {}

        for i, line in enumerate(lines):
            if not any([line.startswith(kw) for kw in self.keywords]):
                command_words[i] = []
                words = get_words(line)

                for word in words:
                    new_cmd_word = CommandWord(word)
                    command_words[i].append(new_cmd_word)

        return command_words


    def annotate_conditional_words(self, command_dict: dict[int, CommandWord], lines: list[str]) -> dict[int, CommandWord]:
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

            if not any([line.startswith(kw) for kw in self.keywords]):
                if if_level > 0 or unless_level > 0:
                    for cmd_word in command_dict[i]:
                        cmd_word.in_conditional = True
                #print(command_dict[i].in_conditional, command_dict[i].text)

        return command_dict

        
    def annotate_loop_words(self, command_dict: dict[int, CommandWord], lines: list[str]) -> dict[int, CommandWord]:
        loop_keywords = ['#for', '#end for', '#while', '#end while']

        for_level = 0
        while_level = 0

        for i, line in enumerate(lines):
            # incremet loop depth levels
            if line.startswith('#for '):
                self.logger.log(2, 'for loop encountered')
                for_level += 1
            if line.startswith('#while '):
                self.logger.log(2, 'for loop encountered')
                while_level += 1

            # decrement loop depth levels
            if '#end for' in line:
                for_level -= 1
            if '#end while' in line:
                while_level -= 1

            if not any([line.startswith(kw) for kw in self.keywords]):
                if for_level > 0 or while_level > 0:
                    for cmd_word in command_dict[i]:
                        cmd_word.in_loop = True
                #print(command_dict[i].in_loop, command_dict[i].text)

        return command_dict


    def convert_to_words(self, command_dict: dict[int, CommandWord]) -> list[CommandWord]:
        command_lines = list(command_dict.items())
        command_lines.sort(key = lambda x: x[0])
        command_lines = [line for num, line in command_lines]
        command_words = [item for word in command_lines for item in word]
        return command_words


    def translate_gx_keywords(self, command_words: list[CommandWord]) -> list[CommandWord]:
        for word in command_words:
            gx_keyword_value = get_galaxy_keyword_value(word.text)
            if gx_keyword_value != None:
                word.text = gx_keyword_value

        return command_words


    def truncate_extra_commands(self, command_words: list[CommandWord]) -> list[CommandWord]:
        first_command_complete = False
        cutoff = -1

        for i, word in enumerate(command_words):
            if word.text == '>':
                if first_command_complete:
                    cutoff = i
                    break
                else:
                    first_command_complete = True

            elif word.text == '|':
                if first_command_complete:
                    cutoff = i
                    break
                else:
                    self.logger.log(2, "pipe encountered as end of 1st command")
                    print()
        
        # truncate or keep all cmd words 
        if cutoff != -1:
            out_words = command_words[:cutoff]
            self.logger.log(1, "multiple commands encountered")
        else:
            out_words = command_words

        return out_words







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

