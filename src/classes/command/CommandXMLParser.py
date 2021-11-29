

# pyright: basic

from collections import defaultdict
import xml.etree.ElementTree as et
import regex as re

from classes.outputs.OutputRegister import OutputRegister
from classes.params.ParamRegister import ParamRegister
from classes.command.AliasExtractor import AliasExtractor
from classes.command.CommandWord  import CommandWord
from classes.logging.Logger import Logger

from utils.regex_utils import find_unquoted, get_words, get_galaxy_keywords, get_galaxy_keyword_value, get_unpaired_quotes_start
from utils.command_utils import remove_ands_from_line

"""
role of this module is to preprocess the command string into a useable state

aim is to remove constructs like cheetah comments, conditional lines without
removing other elements like #set directives which will be used later. 

some stdio stuff is managed here. '| tee ', '|& tee ', 2>&1 etc are found and replaced or just removed for better understanding. 

command string is also de-indented and generally cleaned (blank lines removed etc)

returns list of CommandWords
after this module, the list of CommandWord() gets parsed to CommandProcessor() which processes the words into an actual Command()

"""


class CommandXMLParser:
    def __init__(self, tree: et.ElementTree, param_register: ParamRegister, out_register: OutputRegister, logger: Logger):
        self.tree = tree
        self.param_register = param_register
        self.out_register = out_register
        self.logger = logger
        self.keywords = self.get_keywords()
        self.statement_block = 0
        self.command_string: str = ''


    def get_keywords(self) -> None:
        conditional_keywords = ['#if ', '#else if ', '#elif ', '#else', '#end if', '#unless ', '#end unless']
        loop_keywords = ['#for ', '#end for', '#while ', '#end while']
        error_keywords = ['#try ', '#except', '#end try']
        cheetah_var_keywords = ['#def ', '#set ']
        linux_commands = ['set ', 'ln ', 'cp ', 'mkdir ', 'tar ', 'ls ', 'head ', 'wget ', 'grep ', 'awk ', 'cut ', 'sed ', 'export ', 'gzip ', 'gunzip ', 'cd ', 'echo ', 'trap ', 'touch ']
        return conditional_keywords + loop_keywords + error_keywords + cheetah_var_keywords + linux_commands
        

    def parse(self) -> list[str]:
        """
        NOTE: would potentially be useful to employ lark here
        """
        self.set_command_string()
        self.set_lines()
        self.set_aliases()
        self.set_cmd_words()

    
    def set_command_string(self) -> None:
        command_string = self.get_command_from_xmltree()
        command_string = self.simplify_stdio(command_string)
        self.command_string = self.simplify_galaxy_reserved_words(command_string)
        

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
        

    def set_lines(self) -> None:
        # clean the command string
        lines = self.split_lines(self.command_string)
        lines = self.standardise_variable_format(lines)
        lines = self.remove_comments(lines)
        lines = self.remove_bash_constructs(lines)
        lines = self.remove_cheetah_definitions(lines)
        lines = self.remove_cheetah_misc(lines)
        # TODO experimental
        lines = self.remove_unpaired_quote_text(lines)
        self.lines = lines


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


    def set_aliases(self) -> None:
        ae = AliasExtractor(self.lines, self.param_register, self.out_register, self.logger)
        ae.extract()
        self.alias_register = ae.alias_register


    def set_cmd_words(self) -> None:
        command_words = self.init_command_words()
        command_words = self.translate_gx_keywords(command_words)
        command_words = self.truncate_extra_commands(command_words)
        
        # sentinel
        for statement_block, cmd_words in command_words.items():
            cmd_words.append(CommandWord('__END_COMMAND__', self.statement_block))
        self.command_words = command_words


    def init_command_words(self) -> list[CommandWord]:
        command_words = defaultdict(list)
        self.statement_block = 0
        self.levels = {
            'if': 0,
            'unless': 0,
            'for': 0,
            'while': 0,
        }

        for line in self.lines:
            self.update_levels(line)
            temp_line = remove_ands_from_line(line)

            # ignore anything within a for/while block
            if self.levels['for'] == 0 and self.levels['while'] == 0:
                
                # checks if the line is syntax or statement
                if not any([temp_line.startswith(kw) for kw in self.keywords]):
                    # DO NOT just line.split()
                    # regex used here to ensure quoted strings appear as 
                    # single words etc
                    # TODO could possibly handle multiline strings here?
                    words = get_words(line)  

                    for word in words:
                        if word == '&&' or word == ';':
                            self.statement_block =+ 1
                            continue
                        else:
                            new_cmd_word = CommandWord(word, self.statement_block)
                            new_cmd_word = self.annotate_level_info(new_cmd_word)
                            command_words[self.statement_block].append(new_cmd_word)

        return command_words


    def update_levels(self, line: str) -> None:
        # incrementing
        if line.startswith('#if '):
            self.levels['if'] += 1
        if line.startswith('#unless '):
            self.levels['unless'] += 1
        if line.startswith('#for '):
            self.logger.log(1, 'for loop encountered')
            self.levels['for'] += 1
        if line.startswith('#while '):
            self.logger.log(1, 'for loop encountered')
            self.levels['while'] += 1

        # decrementing
        if '#end if' in line:
            self.levels['if'] -= 1
        if '#end unless' in line:
            self.levels['unless'] -= 1
        if '#end for' in line:
            self.levels['for'] -= 1
        if '#end while' in line:
            self.levels['while'] -= 1


    def annotate_level_info(self, word: CommandWord) -> CommandWord:
        if self.levels['if'] > 0 or self.levels['unless'] > 0:
            word.in_conditional = True
        if self.levels['for'] > 0 or self.levels['while'] > 0:
            word.in_loop = True
        
        return word


    def translate_gx_keywords(self, command_words: list[CommandWord]) -> list[CommandWord]:
        for statement_block, cmd_words in command_words.items():
            for word in cmd_words:
                gx_keywords = get_galaxy_keywords(word.text)
                for keyword in gx_keywords:
                    kw_val = get_galaxy_keyword_value(keyword)
                    word.text = word.text.replace(keyword, kw_val)

        return command_words


    def truncate_extra_commands(self, command_words: list[CommandWord]) -> list[CommandWord]:
        for statement_block, cmd_words in command_words.items():
            first_command_complete = False
            cutoff = -1

            for i, word in enumerate(cmd_words):
                if word.text == '>':
                    if first_command_complete:
                        cutoff = i
                        break
                    else:
                        first_command_complete = True

                elif word.text == '|':
                    if not first_command_complete:
                        self.logger.log(1, "pipe encountered as end of 1st command")
                    cutoff = i
                    break
            
            # truncate or keep all cmd words 
            if cutoff != -1:
                command_words[statement_block] = cmd_words[:cutoff]
                self.logger.log(1, "multiple commands encountered")
            else:
                command_words[statement_block] = cmd_words

        return command_words


    def pretty_print_command_words(self) -> None:
        print('Command Words --------------------------------------------------------------- \n')
        for statement_block, cmd_words in self.command_words.items():
            for word in cmd_words:
                print(f'{word.text[:39]:40}{statement_block:>5}')
        print()

    
    # deprecated
    # def truncate_extra_commands(self, command_words: list[CommandWord]) -> list[CommandWord]:
    #     first_command_complete = False
    #     cutoff = -1

    #     for i, word in enumerate(command_words):
    #         if word.text == '>':
    #             if first_command_complete:
    #                 cutoff = i
    #                 break
    #             else:
    #                 first_command_complete = True

    #         elif word.text == '|':
    #             if first_command_complete:
    #                 cutoff = i
    #                 break
    #             else:
    #                 self.logger.log(2, "pipe encountered as end of 1st command")
        
    #     # truncate or keep all cmd words 
    #     if cutoff != -1:
    #         out_words = command_words[:cutoff]
    #         self.logger.log(0, "multiple commands encountered")
    #     else:
    #         out_words = command_words

    #     return out_words




