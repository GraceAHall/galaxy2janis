


from typing import Tuple


from classes.Logger import Logger
from classes.command.Alias import AliasRegister
from classes.command.Command import TokenType
from classes.command.CommandProcessor import CommandWord
from classes.outputs.OutputRegister import OutputRegister
from classes.params.ParamRegister import ParamRegister

from utils.regex_utils import find_unquoted
from utils.command_utils import init_cmd_word, get_best_token

"""
NOTE
Alias system stripped back.
only stores aliases when they involve a galaxy param or output.

"""


class AliasExtractor:
    def __init__(self, lines: list[str], param_register: ParamRegister, out_register: OutputRegister, logger: Logger):
        self.lines = lines
        self.param_register = param_register
        self.out_register = out_register
        self.logger = logger
        self.alias_register: AliasRegister = AliasRegister()


    def extract(self) -> None:
        """
        finds all aliases in command string. 
        extracts them into AliasRegister which keeps track of aliases
        and allows aliases to be resolved.
        """
              
        for line in self.lines:
            line = self.remove_ands(line)
            self.extract_set_aliases(line)
            self.extract_symlink_aliases(line)
            self.extract_copy_aliases(line)
            

    def remove_ands(self, line: str) -> str:
        line_elems = line.split(' ')
        line_elems = [e for e in line_elems if e != '&&' and e != ';']
        return ' '.join(line_elems)

          
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
            

    def update_aliases(self, left: str, right: str, from_cmd: str, line: str) -> None:
        # get tokens from text
        source = self.init_token_from_text(left)
        dest = self.init_token_from_text(right)

        # update
        if source is not None and dest is not None:
            if dest.type in [TokenType.GX_OUT, TokenType.GX_PARAM]:
                self.alias_register.add(source.text, dest.text, from_cmd, line)
        else:
            self.logger.log(1, f'could not add alias from line: {line}')


    def split_variable_assignment(self, line: str) -> Tuple[str, str]:
        operator_pattern = r'[-+\\/*=]?='
        #print('\n' + line)

        operator_start, operator_end = find_unquoted(line, operator_pattern)
        left, right = line[:operator_start].strip(), line[operator_end:].strip()
        return left, right


    def init_token_from_text(self, text: str) -> CommandWord:
        cmd_word = init_cmd_word(text)
        return get_best_token(cmd_word, self.param_register, self.out_register)

    
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