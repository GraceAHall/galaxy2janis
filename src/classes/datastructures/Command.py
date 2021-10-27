

from typing import Tuple, Optional
import re 

from classes.datastructures.Params import Param

from utils.regex_utils import find_unquoted, extract_cheetah_vars, get_numbers_and_strings



class CommandLine:
    def __init__(self, command_num: str, text: str):
        self.command_num = command_num
        self.text = text
        self.in_loop = False
        self.in_conditional = False


# class CommandVar:
#     def __init__(self):
#         self.type = 


class Token:
    def __init__(self, token_num: str, text: str):
        self.token_num = token_num
        self.text = text


"""
functions needed:
    - get param default value (check whether param is option or an argument)
    - mark param has occurred in command
    - mark params which only have references in conditionals
    - (later) parsed datatypes

"""

class Command:
    def __init__(self, lines: list[str], commands: list[CommandLine], params: list[Param]):
        """
        Command class receives the CommandLines
        """
        self.params = params
        self.lines = lines
        self.commands = commands
        self.tokens: dict[int, Token] = {}
        self.aliases: dict[str, str] = {}


    def process(self):
        self.set_param_cheetah_strings()
        self.set_aliases()
        self.set_tokens() 
        self.identify_options()
        self.set_base_word()


    def set_param_cheetah_strings(self):
        """
        sets the 4 possible cheetah formats for each param variable
        """
        for param in self.params:
            param.gx_var_strings.add(f'${param.gx_var}')
            param.gx_var_strings.add(f'${{{param.gx_var}}}')
            param.gx_var_strings.add(f'"${{{param.gx_var}}}"')
            param.gx_var_strings.add(f"'${{{param.gx_var}}}'")


    def set_aliases(self) -> None:
        """
        finds all aliases in command string. 
        creates an alias dict which maps links between variables. form:
        { 
            '$var1': '$var2',
            '$proteins': '$temp',
            '$in1': '$in1_name',
            '$var1': 'sample.fastq'
        }
        can then query the alias dict to better link galaxy params to variables in command string
        """
       
        alias_dict: dict[str, str] = {}
        
        for line in self.lines:
            aliases = []
            aliases += self.extract_set_aliases(line)
            aliases += self.extract_symlink_aliases(line)
            aliases += self.extract_copy_aliases(line)
            aliases += self.extract_for_aliases(line)
            aliases += self.extract_env_aliases(line)
            for source, dest in aliases:
                alias_dict[source] = dest

        return alias_dict

            

    def extract_set_aliases(self, line: str) -> list[Tuple[str, str]]:
        """
        examples:
        #set var2 = $var1
        #set $ext = '.fastq.gz'
        #set temp = $to_string($proteins)
        #set $safename = re.sub('[^\w\-_\.]', '_', $report.element_identifier)
        #set $control_sample = str($control_sample).strip()
        #set $rg_pu = $rg_param("PU")
        """
        
        aliases = []
        
        if line.startswith('#set '):
            # split the line at the operator and trim
            left, right = self.split_set_direc(line)
            
            # set the source
            source = self.get_set_source(left)
            
            # set the dest
            dest = self.get_set_dest(right)

            print(f'{source} --> {dest}')       
            
        return aliases


    def split_set_direc(self, line: str) -> Tuple[str, str]:
        operator_pattern = r'[+-\\/*=]?='
        print('\n' + line)

        line = line[5:] # removes the '#set ' from line start
        operator_start, operator_end = find_unquoted(line, operator_pattern)
        left, right = line[:operator_start].strip(), line[operator_end:].strip()
        return left, right


    def get_set_source(self, source_str: str) -> str:
        source = None
        source_str = '$' + source_str if not source_str.startswith('$') else source_str
        source_vars = extract_cheetah_vars(source_str)
        assert(len(source_vars) == 1)
        source = source_vars[0]
        return source


    def get_set_dest(self, dest_str: str) -> Optional[str]:
        # set the dest
        dest_vars = extract_cheetah_vars(dest_str)
        dest_vars = self.remove_common_modules(dest_vars)

        dest = None
        if len(dest_vars) == 1:
            dest = dest_vars[0]

        elif len(dest_vars) == 0:
            dest_literals = get_numbers_and_strings(dest_str)
            if len(dest_literals) == 1:
                dest = dest_literals[0] 

        return dest            

        
    def remove_common_modules(self, var_list: list[str]) -> list[str]:
        common_modules = {'$re'}
        
        out_vars = []
        for var in var_list:
            if not var in common_modules:
                out_vars.append(var)

        return out_vars

    
    def extract_symlink_aliases(self, line: str) -> list[Tuple[str, str]]:
        """
        ln -s '$in1' '$in1_name'
        ln -s '$in1' sample.fasta
        """
        aliases = []
        if ' ln ' in line or line.startswith('ln '):
            source, dest = line.split(' ')[-2:]
            print(line)
            print(f'{source} --> {dest}')
            print()
        return aliases


    def extract_copy_aliases(self, line: str) -> list[Tuple[str, str]]:
        """
        cp $var1 sample.fastq
        """
        aliases = []
        
        if line.startswith('cp '):
            source, dest = line.rsplit(' ', 2)[-2:]
            # TODO here
            temp = extract_cheetah_vars(source)
            print()
        
        return aliases


    def extract_for_aliases(self, line: str) -> list[Tuple[str, str]]:
        """
        #for $bed in $names.beds
        """
        aliases = []
        return aliases


    def extract_env_aliases(self, line: str) -> list[Tuple[str, str]]:
        """
        export TERM=vt100
        export AUGUSTUS_CONFIG_PATH=`pwd`/augustus_dir/ &&
        """
        aliases = []
        return aliases


    def set_tokens(self) -> None:
        """
        - is the token  --option=arg / -option:arg ect?
            - break into an option. 
            - next.
        - does the token start with '-'?
            - label as option
            - does the next token start with not '-'?
                - try to resolve it as a galaxy param. 
                - if possible and the param default value starts with '-'
                    - next (next token is also an option)
                - else
                    - set the next token as the option argument
        - else
            - try to resolve it as a galaxy param. 
            - if possible and the param default value starts with '-'
                - label as option
            - else
                - positional arg
        """