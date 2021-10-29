

from typing import DefaultDict, Tuple, Optional
from collections import defaultdict
from enum import Enum
import re

from regex.regex import finditer 

from classes.datastructures.Params import Param

from utils.regex_utils import (
    find_unquoted,
    get_cheetah_vars, 
    get_numbers_and_strings, 
    get_quoted_numbers,
    get_raw_numbers,
    get_quoted_strings,
    get_raw_strings,
    get_linux_operators,
    get_galaxy_keywords
)


class CommandWord:
    def __init__(self, command_num: str, text: str):
        self.command_num = command_num
        self.text = text
        self.in_loop = False
        self.in_conditional = False
        self.is_keyval = False
        self.keyval_pos = 0
        self.expanded_text: list[str] = []


class Alias:
    def __init__(self, source: str, dest: str, instruction: str, text: str):
        self.source = source
        self.dest = dest
        self.instruction = instruction
        self.text = text


class TokenTypes(Enum):
    GX_VAR           = 1
    QUOTED_STRING   = 2
    RAW_STRING      = 3
    QUOTED_NUM      = 4
    RAW_NUM         = 5
    LINUX_OP        = 6
    GX_KEYWORD      = 7
    

class Token:
    def __init__(self, text: str, token_type: str):
        self.type = token_type.name
        self.text = text
    


"""
AliasRegister stores the aliases we discover while parsing command string
Facilitates 
    adding new aliases to the register
    returing the aliases

This whole class needs to be written cleaner
Started with simple logic but quickly expanded
"""
class AliasRegister:
    def __init__(self, params: dict[str, Param]):
        # parsed galaxy params. needed to resolve aliases to a param. 
        self.gx_params = params

        # stores the aliases using alias.source as key
        # each source may actually have more than 1 alias if different dests
        self.alias_dict: dict[str, list[Alias]] = defaultdict(list)


    def add(self, source: str, dest: str, instruction: str, text: str) -> None:
        # check its not referencing itself
        if source != dest:
            known_aliases = self.alias_dict[source]
            if not any([dest == al.dest for al in known_aliases]):
                # if valid, create new alias and store
                new_alias = Alias(source, dest, instruction, text)
                self.alias_dict[new_alias.source].append(new_alias)


    def template(self, query_string: str) -> list[str]:
        """
        given a query string, templates first var with aliases. 
        ASSUMES ONLY 1 ALIAS IN STRING. otherwise this would get a little recursive. 
        returns list of all possible forms of the query string
        """

        out = []

        for source in self.alias_dict.keys():
            # in case the var has curly braces in text
            patterns = [source, '${' + source[1:] + '}']

            for patt in patterns:
                pattern = re.compile(f'\{patt}(?![\w])')
                res = re.finditer(pattern, query_string)
                matches = [m for m in res]
                if len(matches) > 0:
                    possible_values = self.resolve(source)

                    # may be multiple resolved values.
                    for val in possible_values:
                        for m in matches:
                            supp_query_string = query_string[:m.start()] + val + query_string[m.end():]
                            out.append(supp_query_string)
                    
                    return out

        return [query_string]



    def resolve(self, query_var: str) -> list[str]:
        """
        returns list of all gx vars, and literals that are linked to the query_var
        cheetah vars should be fully resolved here 
        """
        aliases = self.alias_dict[query_var]
        out = []

        for alias in aliases:
            # cheetah or galaxy var
            if alias.dest.startswith('$'):
                # add if galaxy param
                if alias.dest in self.gx_params:
                    out.append(alias.dest)

                # sometimes its weird.
                # eg '$single_paired.paired_input.forward'
                # this is actually an attribute (forward mate pair) of $single_paired.paired_input
                # temp solution: strip common galaxy attributes and try again
                stripped_var = self.strip_gx_attributes(alias.dest)
                if stripped_var in self.gx_params:
                    out.append(stripped_var)

                # recursive. resolves next link if ch or gx var
                out += self.resolve(alias.dest)
                print()
            
            # literal
            else:
                out.append(alias.dest)

        return out


    def strip_gx_attributes(self, the_string: str) -> str:
        gx_attributes = [
            '.forward',
            '.reverse',
            '.ext',
            '.value',
            '',
        ]


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
        self.restructure_params()
        self.lines = lines
        self.command_lines = command_lines
        self.command_words = [item for word in command_lines for item in word]
        self.aliases: AliasRegister = AliasRegister(self.params)
        self.env_vars: list[str] = []
        self.options: list[Option] = []


    def restructure_params(self) -> None:
        param_dict = {}
        for p in self.params:
            key = '$' + p.gx_var
            param_dict[key] = p
        self.params = param_dict


    def process(self):
        self.extract_env_vars()
        self.set_aliases()
        self.expand_aliases()
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
              
        for line in self.lines:
            self.extract_set_aliases(line)
            self.extract_symlink_aliases(line)
            self.extract_copy_aliases(line)
            
            # a little confused on mv at the moment. leaving. 
            #self.extract_mv_aliases(line)
            
            # #for aliases actually could be supported v0.1
            # would only be the simple case where you're unpacking an array (#for $item in $param:)
            
            #self.extract_for_aliases(line)

          
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
            
            # set the source
            source = self.get_source(left)
            
            # set the dest
            dest = self.get_dest(right)

            #print(f'{source} --> {dest}')
            if source is not None and dest is not None:
                self.aliases.add(source, dest, 'set', line)
            


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
        
        source_vars = get_cheetah_vars(source_str)
        assert(len(source_vars) == 1)
        source = source_vars[0]
        return source


    def get_dest(self, dest_str: str) -> Optional[str]:
        # any cheetah vars?
        dest_vars = get_cheetah_vars(dest_str)
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

    
    def extract_symlink_aliases(self, line: str) -> None:
        """
        NOTE - dest and source are swapped for symlinks.
        """
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
                self.aliases.add(source, dest, 'ln', line) 


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
            arg1, arg2 = line.split(' ')[-2:]
            # set the source
            dest = self.get_source(arg1)
            
            # set the dest
            source = self.get_dest(arg2)

            #print(line)
            #print(f'{source} --> {dest}')
            if source is not None and dest is not None:
                self.aliases.add(source, dest, 'cp', line)  
        


    def extract_mv_aliases(self, line: str) -> list[Tuple[str, str]]:
        """
        mv ${output_dir}/summary.tab '$output_summary'
        mv '${ _aligned_root }.2${_aligned_ext}' '$output_aligned_reads_r'
        mv circos.svg ../
        mv circos.svg outputs/circos.svg

        mv input_file.tmp output${ ( $i + 1 ) % 2 }.tmp
        
        """
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
                self.aliases.add(source, dest, 'mv', line) 


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


    def expand_aliases(self) -> None:
        for cmd_word in self.command_words:
            cmd_forms = self.aliases.template(cmd_word.text)
            cmd_word.expanded_text = cmd_forms


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


    def identify_options(self) -> None:
        """
        filtlong
        --target_bases '$output_thresholds.target_bases'
        minid='$adv.min_dna_id'
        -t\${GALAXY_SLOTS:-4} (no sep between flag and arg)
        '$input_file' > output.fastq
        """
        cmd_count = 0
        print('\n')
        for i in range(len(self.command_words) - 1):
            curr_word = self.command_words[i]
            next_word = self.command_words[i+1]

            # positional literal, option_flag + option_arg, key=val pair
            cmd_type = self.get_command_type(curr_word, next_word)

            if cmd_type == 'positional':
                pass

            if cmd_type == 'kv_pair':
                pass

            if cmd_type == 'flag':
                pass

            if cmd_type == 'option':
                pass

        self.handle_last_cmd_word(self.command_words[-1])


    def get_command_type(self, curr_word: CommandWord, next_word: CommandWord) -> str:

        #print(curr_word.text, ':')
        for form in curr_word.expanded_text:
            curr_tokens = self.get_tokens(form)
            #curr_token = self.select_highest_priority_token()
            for t in curr_tokens:
                print(f'{t.type:20s}{t.text}')
            
        for form in next_word.expanded_text:
            next_tokens = self.get_tokens(form)
          
        # positional

        # flag

        # option

        # TODO kv_pair (key=val construct) ???
        return


    def get_tokens(self, text: str) -> list[str]:
        """
        detects the type of object being dealt with.
        first task is to resolve any aliases or env_variables. 

        can be:
            literal
                - starts with alphanumeric
            literal flag 
                - starts with '-'
            gx_var
                - has galaxy var in the word
        """  

        tokens = []

        quoted_num_lits = get_quoted_numbers(text)
        tokens += [Token(m, TokenTypes.QUOTED_NUM) for m in quoted_num_lits]

        quoted_str_lits = get_quoted_strings(text)
        # remove quoted cheetah vars
        quoted_str_lits = [m for m in quoted_str_lits if m[1] != '$']
        tokens += [Token(m, TokenTypes.QUOTED_STRING) for m in quoted_str_lits]
        
        raw_num_lits = get_raw_numbers(text)
        tokens += [Token(m, TokenTypes.RAW_NUM) for m in raw_num_lits]
        
        raw_str_lits = get_raw_strings(text)
        tokens += [Token(m, TokenTypes.RAW_STRING) for m in raw_str_lits]
        
        # quoted or not doesn't matter. just linking. can resolve its datatype later. 
        ch_vars = get_cheetah_vars(text)
        gx_vars = [x for x in ch_vars if x in self.params]
        tokens += [Token(var, TokenTypes.GX_VAR) for var in gx_vars]

        # TODO this is pretty weak. actually want to search for 
        # unquoted operator in word. split if necessary. 
        linux_operators = get_linux_operators(text)
        tokens += [Token(op, TokenTypes.LINUX_OP) for op in linux_operators]

        gx_keywords = get_galaxy_keywords(text)
        tokens += [Token(kw, TokenTypes.GX_KEYWORD) for kw in gx_keywords]
        
        assert(len(tokens) == 1)
        return tokens


        
        
    def split_keyval_cmd(self, cmd_word: str) -> list[str]:
        """
        handles normal words and the following patterns:
        --minid=$adv.min_dna_id
        --protein='off'
        ne=$ne
        """
        if '=' in cmd_word:
            operator_start, operator_end = find_unquoted(cmd_word, '=')
            flag, arg = cmd_word[:operator_start], cmd_word[operator_end:]
            return [flag, arg]
        else:
            return [cmd_word]


    def set_base_word():
        pass