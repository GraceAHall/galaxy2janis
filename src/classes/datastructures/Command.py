

from typing import Tuple, Optional
import re 

from classes.datastructures.Params import Param

from utils.regex_utils import find_unquoted, extract_cheetah_vars, get_numbers_and_strings, get_raw_strings


class CommandWord:
    def __init__(self, command_num: str, text: str):
        self.command_num = command_num
        self.text = text
        self.in_loop = False
        self.in_conditional = False


class Alias:
    def __init__(self, text: str, source: str, dest: str, instruction: str):
        self.text = text
        self.source = source
        self.dest = dest
        self.instruction = instruction


class Option:
    def __init__(self, ident: int, text: str):
        self.id: int = ident
        self.flag: str = ''
        self.args: set[str] = set()
        


class Command:
    def __init__(self, lines: list[str], command_lines: list[list[CommandWord]], params: list[Param]):
        """
        Command class receives the CommandLines
        """
        self.params = params
        self.lines = lines
        self.command_lines = command_lines
        self.command_words = [item for word in command_lines for item in word]
        self.aliases: dict[str, str] = {}
        self.env_vars: list[str] = []
        self.options: list[Option] = []


    def process(self):
        self.set_param_cheetah_strings()
        self.set_aliases()
        self.extract_env_vars()
        self.print_command_lines()
        # NOTE - preserving the line structure of command is temporary
        # only used for visual checks
        # this transformation is much better
        self.print_command_words()
        self.identify_options()
        self.set_base_word()


    def print_command_lines(self) -> None:
        print()
        for line in self.command_lines:
            for cmd_word in line:
                temp_str = f'[{cmd_word.command_num}]'
                if cmd_word.in_conditional:
                    temp_str += '[C]'
                if cmd_word.in_loop:
                    temp_str += '[L]'
                temp_str += cmd_word.text
                print(temp_str, end=' ')
            print()


    def print_command_words(self) -> None:
        print()
        print(f'{"word":60s}{"pos":>6}{"cond":>6}{"loop":>6}')
        for word in self.command_words:
            print(f'{word.text:60s}{word.command_num:6d}{word.in_conditional:6}{word.in_loop:6}')
        
    # TODO unnecessary?
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
            
            # a little confused on mv at the moment. leaving. 
            #aliases += self.extract_mv_aliases(line)
            
            # #for aliases actually could be supported v0.1
            # would only be the simple case where you're unpacking an array (#for $item in $param:)
            
            #aliases += self.extract_for_aliases(line)
            for al in aliases:
                alias_dict[al.source] = al


        # remove self-referencing aliases (yes this can happen)
        to_delete = []
        for source, alias in alias_dict.items():
            if source == alias.dest:
                to_delete.append(source)

        for item in to_delete:
            del alias_dict[item]

        return alias_dict

            

    def extract_set_aliases(self, line: str) -> list[Alias]:
        """
        examples:
        #set var2 = $var1
        #set $ext = '.fastq.gz'
        """
        
        aliases = []
        
        if line.startswith('#set '):
            # split the line at the operator and trim
            left, right = self.split_variable_assignment(line)
            left = left[5:] # removes the '#set ' from line start
            
            # set the source
            source = self.get_source(left)
            
            # set the dest
            dest = self.get_dest(right)

            #print(f'{source} --> {dest}')
            if source is not None and dest is not None:
                new_alias = Alias(line, source, dest, 'set')
                aliases.append(new_alias)     
            
        return aliases


    def split_variable_assignment(self, line: str) -> Tuple[str, str]:
        operator_pattern = r'[-+\\/*=]?='
        #print('\n' + line)

        operator_start, operator_end = find_unquoted(line, operator_pattern)
        left, right = line[:operator_start].strip(), line[operator_end:].strip()
        return left, right


    def get_source(self, source_str: str) -> str:
        source = None
        if not source_str[0] in ['"', "'"]:
            if source_str[0] != '$':
                source_str = '$' + source_str
        
        source_vars = extract_cheetah_vars(source_str)
        assert(len(source_vars) == 1)
        source = source_vars[0]
        return source


    def get_dest(self, dest_str: str) -> Optional[str]:
        # any cheetah vars?
        dest_vars = extract_cheetah_vars(dest_str)
        dest_vars = self.remove_common_modules(dest_vars)

        # any literals?
        dest_literals = get_numbers_and_strings(dest_str)

        # raw strings?
        dest_raw_strings = get_raw_strings(dest_str)

        # case: single cheetah var      
        if len(dest_vars) == 1:
            return dest_vars[0]
        elif len(dest_vars) > 1:
            return None

        # case: single literal
        if len(dest_literals) == 1:
            return dest_literals[0]
        elif len(dest_literals) > 1:
            return None

        # case: single raw string (alphanumeric symbol)
        if len(dest_raw_strings) == 1:
            return dest_raw_strings[0]

        return None           

        
    def remove_common_modules(self, var_list: list[str]) -> list[str]:
        common_modules = {'$re'}
        
        out_vars = []
        for var in var_list:
            if not var in common_modules:
                out_vars.append(var)

        return out_vars

    
    def extract_symlink_aliases(self, line: str) -> list[Tuple[str, str]]:
        """
        NOTE - dest and source are swapped for symlinks.
        """
        aliases = []
        if line.startswith('ln '):
            arg1, arg2 = line.split(' ')[-2:]

            # for ln syntax where only FILE is given (no DEST)
            if arg1.startswith('-'):
                arg1 = arg2

            # set the source
            dest = self.get_source(arg1)
            
            # set the dest
            source = self.get_dest(arg2)

            #print(line)
            #print(f'{source} --> {dest}')
            if source is not None and dest is not None:
                new_alias = Alias(line, source, dest, 'ln')
                aliases.append(new_alias)   

        return aliases


    def extract_copy_aliases(self, line: str) -> list[Tuple[str, str]]:
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
        aliases = []
        
        if line.startswith('cp '):
            arg1, arg2 = line.split(' ')[-2:]
            # set the source
            dest = self.get_source(arg1)
            
            # set the dest
            source = self.get_dest(arg2)

            #print(line)
            #print(f'{source} --> {dest}')
            if source is not None and dest is not None:
                new_alias = Alias(line, source, dest, 'cp')
                aliases.append(new_alias)   
        
        return aliases


    def extract_mv_aliases(self, line: str) -> list[Tuple[str, str]]:
        """
        mv ${output_dir}/summary.tab '$output_summary'
        mv '${ _aligned_root }.2${_aligned_ext}' '$output_aligned_reads_r'
        mv circos.svg ../
        mv circos.svg outputs/circos.svg

        mv input_file.tmp output${ ( $i + 1 ) % 2 }.tmp
        
        """
        aliases = []
        if line.startswith('mv '):
            arg1, arg2 = line.split(' ')[-2:]

            # for ../ where we move the fileyntax where only FILE is given (no DEST)
            if arg1.startswith('-'):
                arg1 = arg2

            # set the source
            dest = self.get_source(arg1)
            
            # set the dest
            source = self.get_dest(arg2)

            #print(line)
            #print(f'{source} --> {dest}')
            if source is not None and dest is not None:
                new_alias = Alias(line, source, dest, 'ln')
                aliases.append(new_alias)   

        return aliases


    # develop later. too complex. 
    # def extract_for_aliases(self, line: str) -> list[Tuple[str, str]]:
    #     """
    #     #for $bed in $names.beds
    #     #for i, e in enumerate($input_cond.inS)
    #     #for $i in $input_format_cond.input:
    #         --input '${i}' '${i.hid}'

    #     """
    #     # use match groups? 
    #     aliases = []
    #     return aliases


    def extract_env_vars(self) -> None:
        """
        export TERM=vt100
        export AUGUSTUS_CONFIG_PATH=`pwd`/augustus_dir/ &&
        export BCFTOOLS_PLUGINS=`which bcftools | sed 's,bin/bcftools,libexec/bcftools,'`;
        export MPLCONFIGDIR=\$TEMP &&
        export JAVA_OPTS="-Djava.awt.headless=true -Xmx\${GALAXY_MEMORY_MB:-1024}m"
        `pwd` -> set this as a known function? 
        """
        env_vars = []

        for line in self.lines:

            if line.startswith('export '):
                left, right = self.split_variable_assignment(line)
                left = left[7:] # removes the 'export ' from line start

                # set the source
                source = self.get_source(left)
                dest = None # not even gonna worry about what it means. just marking as exists
            
                if source is not None:
                    env_vars.append(source) 

        self.env_vars = env_vars


    def identify_options():
        """
        filtlong    
        --target_bases 
        '$output_thresholds.target_bases' 
        --keep_percent  
        '$output_thresholds.keep_percent'
        """
        pass


    def set_base_word():
        pass