
# pyright: basic

from __future__ import annotations
from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from classes.tool.Tool import Tool


from classes.logging.Logger import Logger
from classes.command.Alias import AliasRegister
from classes.command.Tokens import Token, TokenType

from utils.regex_utils import find_unquoted, get_simple_strings
from utils.token_utils import tokenify, split_line_by_ands


"""
NOTE
Alias system stripped back.
only stores aliases when they involve a galaxy param or output.

"""


class AliasExtractor:
    def __init__(self, command_lines: list[str], tool: Tool, logger: Logger):
        self.command_lines = command_lines
        self.tool = tool
        self.logger = logger
        self.alias_register: AliasRegister = AliasRegister()


    def extract(self) -> None:
        """
        finds all aliases in command string. 
        extracts them into AliasRegister which keeps track of aliases
        and allows aliases to be resolved.
        """
              
        for line in self.command_lines:
            sublines = split_line_by_ands(line)
            for subline in sublines:
                self.extract_set_aliases(subline)
                self.extract_symlink_aliases(subline)
                self.extract_copy_aliases(subline)
            
          
    def extract_set_aliases(self, line: str) -> None:
        """
        examples:
        #set var2 = $var1
        #set $ext = '.fastq.gz'
        """

        if line.startswith('#set '):
            # split the line at the operator and trim
            left, right = self.split_variable_assignment(line)
            left = left[5:] # removes the '#set ' from line start
            self.update_aliases(left, right, 'set', line)  


    def split_variable_assignment(self, line: str) -> Tuple[str, str]:
        operator_pattern = r'[-+\\/*=]?='
        #print('\n' + line)

        operator_start, operator_end = find_unquoted(line, operator_pattern)
        left, right = line[:operator_start].strip(), line[operator_end:].strip()
        return left, right

            
    def update_aliases(self, left: str, right: str, from_cmd: str, line: str) -> None:
        # get tokens from text
        source = self.init_token_from_text(left)
        dest = self.init_token_from_text(right)

        # update
        if source is not None and dest is not None:
            # destination is a know galaxy object
            if dest.type in [TokenType.GX_OUT, TokenType.GX_PARAM]:
                self.alias_register.add(source.text, dest.text, from_cmd, line)

            # destination is a number
            elif dest.type in [TokenType.RAW_NUM, TokenType.QUOTED_NUM]:
                self.alias_register.add(source.text, dest.text, from_cmd, line)

            # destination is a string but its very simple looking
            elif dest.type in [TokenType.RAW_STRING, TokenType.QUOTED_STRING]:
                if self.string_is_polite(dest.text):
                    self.alias_register.add(source.text, dest.text, from_cmd, line)

        else:
            self.logger.log(1, f'could not add alias from line: {line}')


    def init_token_from_text(self, text: str) -> Token:
        token = tokenify(text, param_register=self.tool.param_register, out_register=self.tool.out_register)
        if token == None:
            self.logger.log(1, f'can resolve token {text}')
        return token


    def string_is_polite(self, text: str) -> bool:
        simple_strings = get_simple_strings(text)
        if len(simple_strings) == 1 and simple_strings[0] == text:
            return True
        return False

    
    def extract_symlink_aliases(self, line: str) -> None:
        """
        NOTE - dest and source are swapped for symlinks.
        """
        if line.startswith('ln '):
            left, right = line.split(' ')[-2:]

            # for ln syntax where only FILE is given (no DEST)
            if left.startswith('-'):
                left = right

            self.update_aliases(right, left, 'ln', line)  


    def extract_copy_aliases(self, line: str) -> None:
        """
        NOTE - dest and source are swapped for cp commands.

        basically the same as symlinks, just checking if cp command in line
        handling cp commands can be tricky:

            cp '$hd5_format.in.matrix' 'mtx/matrix.mtx'
            cp -r "\$AUGUSTUS_CONFIG_PATH/" augustus_dir/
            cp busco_galaxy/short_summary.*.txt BUSCO_summaries/
            cp '$test_case_conf' circos/conf/galaxy_test_case.json
            #for $hi, $data in enumerate($sec_links.data):
                cp '${data.data_source}' circos/data/links-${hi}.txt
        """       
        if line.startswith('cp '):
            left, right = line.split(' ')[-2:]
            self.update_aliases(right, left, 'cp', line) 