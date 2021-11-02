

import sys
from typing import Tuple, Optional


from classes.datastructures.Command import Command, Token, TokenTypes
from classes.datastructures.Alias import AliasRegister
from classes.datastructures.Params import Param
from classes.datastructures.Outputs import Output
from classes.Logger import Logger

from utils.regex_utils import (
    find_unquoted,
    get_cheetah_vars, 
    get_numbers_and_strings, 
    get_quoted_numbers,
    get_raw_numbers,
    get_quoted_strings,
    get_raw_strings,
    get_linux_operators,
    get_galaxy_keywords,
    get_keyval_pairs
)



class CommandWord:
    def __init__(self, command_num: str, text: str):
        self.command_num = command_num
        self.text = text
        self.in_loop = False
        self.in_conditional = False
        self.expanded_text: list[str] = []


class CommandProcessor:
    def __init__(self, lines: list[str], command_lines: list[list[CommandWord]], params: list[Param], outputs: list[Output], logger: Logger):
        """
        Command class receives the CommandLines
        """
        self.params = params
        self.outputs = outputs
        self.restructure_params()
        self.restructure_outputs()
        self.logger = logger
        self.lines = lines
        self.command_lines = command_lines
        self.command_words = [item for word in command_lines for item in word]
        self.command_words.append(CommandWord(-1, '__END_COMMAND__')) # sentinel for end of command
        self.aliases: AliasRegister = AliasRegister(self.params)
        self.env_vars: list[str] = []


    def restructure_params(self) -> None:
        param_dict = {}
        for p in self.params:
            key = '$' + p.gx_var
            param_dict[key] = p
        self.params = param_dict
    
    
    def restructure_outputs(self) -> None:
        output_dict = {}
        for out in self.outputs:
            key = '$' + out.gx_var
            output_dict[key] = out
        self.outputs = output_dict


    def process(self) -> Command:
        self.extract_env_vars()
        self.set_aliases()
        self.expand_aliases()
        #self.print_command_lines()
        #self.print_command_words()
        command = self.gen_command()
        return command


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


    def gen_command(self) -> None:
        """
        Too big! 
        lots of logic here
            - the command string words are handled one at a time
            - for each command word, lookahead to next word for some context
            - decide whether the current word is positional, flag, option, linux op etc
            - init appropriate object and store
        """

        command = Command()
        positional_count = 0
        is_after_options = False
        i = 0

        # iterate through command words (with next word for context)
        while i < len(self.command_words) - 1:
            curr_word = self.command_words[i]
            next_word = self.command_words[i+1]

            # TODO situations with more than 1!
            if len(curr_word.expanded_text) > 1:
                self.logger.log(2, 'multiple expanded forms of cmd word')
                sys.exit()

            # get best token representation of curr_word
            curr_tokens = self.get_tokens(curr_word.expanded_text[0])
            if len(curr_tokens) == 0:
                self.logger.log(2, 'could not resolve token')
                sys.exit()
            curr_token = self.select_highest_priority_token(curr_tokens)
            
            # get best token representation of next_word
            next_tokens = self.get_tokens(next_word.expanded_text[0])
            if len(next_tokens) == 0:
                self.logger.log(2, 'could not resolve token')
                sys.exit()
            next_token = self.select_highest_priority_token(next_tokens)
            
            # transfer in_conditional status to token
            curr_token.in_conditional = curr_word.in_conditional
            next_token.in_conditional = next_word.in_conditional

            # if kv pair, break and reassign curr/next tokens
            kv_pair = False
            if self.is_kv_pair(curr_token): 
                kv_pair = True
                key, val = self.split_keyval_cmd(curr_token.value)
                curr_token = self.get_tokens(key)[0]
                next_token = self.get_tokens(val)[0]
                next_token.in_conditional = curr_word.in_conditional

            if self.is_linux_op(curr_token, next_token):
                command.update_positionals(positional_count, curr_token, is_after_options)                
                positional_count += 1

            elif self.is_flag(curr_token, next_token):
                is_after_options = True
                command.update_flags(curr_token)

            elif self.is_option(curr_token, next_token):
                is_after_options = True
                command.update_options(curr_token, next_token)
                if not kv_pair:
                    i += 1

            else:
                # text positional
                # this has to happen last, as last resort
                # some examples of options which don't start with '-' exist. 
                command.update_positionals(positional_count, curr_token, is_after_options)                
                positional_count += 1

            i += 1
        return command


    def get_tokens(self, text: str) -> list[Token]:
        """
        detects the type of object being dealt with.
        first task is to resolve any aliases or env_variables. 

        can be:
            literal
                - starts with alphanumeric
            literal flag 
                - starts with '-'
            GX_PARAM
                - has galaxy var in the word
        """  

        tokens = []

        if text == '__END_COMMAND__':
            return [Token('', TokenTypes.END_COMMAND)]

        quoted_num_lits = get_quoted_numbers(text)
        tokens += [Token(m, TokenTypes.QUOTED_NUM) for m in quoted_num_lits]

        quoted_str_lits = get_quoted_strings(text)
        tokens += [Token(m, TokenTypes.QUOTED_STRING) for m in quoted_str_lits]
        
        raw_num_lits = get_raw_numbers(text)
        tokens += [Token(m, TokenTypes.RAW_NUM) for m in raw_num_lits]
        
        raw_str_lits = get_raw_strings(text)
        tokens += [Token(m, TokenTypes.RAW_STRING) for m in raw_str_lits]
        
        # galaxy inputs
        # quoted or not doesn't matter. just linking. can resolve its datatype later. 
        ch_vars = get_cheetah_vars(text)
        gx_params = [x for x in ch_vars if x in self.params]
        gx_params = [self.params[p] for p in gx_params]
        tokens += [Token(param, TokenTypes.GX_PARAM) for param in gx_params]
        
        # galaxy 
        ch_vars = get_cheetah_vars(text) # get cheetah vars
        gx_out = [x for x in ch_vars if x in self.outputs]  # subsets to galaxy out vars
        gx_out = [self.outputs[out] for out in gx_out] # get Output from galaxy out var
        tokens += [Token(out, TokenTypes.GX_OUT) for out in gx_out]  # transform to tokens

        # TODO this is pretty weak. actually want to search for 
        # unquoted operator in word. split if necessary. 
        linux_operators = get_linux_operators(text)
        tokens += [Token(op, TokenTypes.LINUX_OP) for op in linux_operators]

        gx_keywords = get_galaxy_keywords(text)
        tokens += [Token(kw, TokenTypes.GX_KEYWORD) for kw in gx_keywords]

        kv_pairs = get_keyval_pairs(text)
        tokens += [Token(kv, TokenTypes.KV_PAIR) for kv in kv_pairs]
        
        return tokens

    
    def select_highest_priority_token(self, tokens: list[Token]) -> Token:
        # extremely simple. just the token with longest text match.
        # solves issues of galaxy param being embedded in string. 
       
        kv_pairs = [t for t in tokens if t.type == TokenTypes.KV_PAIR]
        gx_params = [t for t in tokens if t.type == TokenTypes.GX_PARAM]
        gx_outs = [t for t in tokens if t.type == TokenTypes.GX_OUT]
        gx_kws = [t for t in tokens if t.type == TokenTypes.GX_KEYWORD]
        linux_ops = [t for t in tokens if t.type == TokenTypes.LINUX_OP]

        if len(kv_pairs) > 0:
            return kv_pairs[0]
        elif len(gx_params) > 0:
            return gx_params[0]
        elif len(gx_outs) > 0:
            return gx_outs[0]
        elif len(gx_kws) > 0:
            return gx_kws[0]
        elif len(linux_ops) > 0:
            return linux_ops[0]
                
        return tokens[0]


    def is_linux_op(self, curr_token: Token, next_token: Token) -> bool:
        """
        """
        if curr_token.type == TokenTypes.LINUX_OP:
            return True
        return False


    def is_kv_pair(self, curr_token: Token) -> bool:
        """
        https://youtu.be/hqVJpfFkJ9k
        """
        if curr_token.type == TokenTypes.KV_PAIR:
            return True
        return False


    def is_flag(self, curr_token: Token, next_token: Token) -> bool:
        # is this a raw flag or option?
        # could be a raw string or galaxy param with flag as default value 
        curr_is_gx_flag = self.get_gx_flag_status(curr_token)
        curr_is_raw_flag = curr_token.type == TokenTypes.RAW_STRING and curr_token.value.startswith('-')

        # the current token has to be a flag 
        if curr_is_raw_flag or curr_is_gx_flag:
            next_is_gx_flag = self.get_gx_flag_status(next_token)
            next_is_raw_flag = next_token.type == TokenTypes.RAW_STRING and next_token.value.startswith('-')

            # next token is a flag
            if next_is_raw_flag or next_is_gx_flag:
                return True

            # next token is linux operation
            elif next_token.type == TokenTypes.LINUX_OP:
                return True
            
            # next token is key-val pair
            elif next_token.type == TokenTypes.KV_PAIR:
                return True
            
            # this is the last command token
            elif next_token.type == TokenTypes.END_COMMAND:
                return True
                
        return False


    def get_gx_flag_status(self, token: Token) -> bool:
        if token.type == TokenTypes.GX_PARAM:
            param = token.value
            # check if numbers first
            if len(get_quoted_numbers(param.default_value)) > 0:
                return False
            elif len(get_raw_numbers(param.default_value)) > 0:
                return False

            # then interpret as string
            elif param.default_value.startswith('-'):
                return True
        
        return False


    def is_option(self, curr_token: Token, next_token: Token) -> bool:
        # happens 2nd after 'is_flag()'
        # already know that its not a flag, so if the current token
        # looks like a flag/option, it has to be an option. 

        curr_is_gx_flag = self.get_gx_flag_status(curr_token)
        curr_is_raw_flag = curr_token.type == TokenTypes.RAW_STRING and curr_token.value.startswith('-')

        # the current token has to be a flag 
        if curr_is_raw_flag or curr_is_gx_flag:
            return True
                
        return False


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


