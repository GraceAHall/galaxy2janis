

import sys
from typing import Tuple, Optional


from classes.datastructures.Command import Command, Token, TokenTypes
from classes.datastructures.Alias import AliasRegister
from classes.datastructures.Params import Param, SelectParam, BoolParam
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
    def __init__(self, text: str):
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
        self.cmd_words = [item for word in command_lines for item in word]
        self.cmd_words.append(CommandWord('__END_COMMAND__')) # sentinel for end of command
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
        self.tokenify_command()
        self.expand_galaxy_tokens()
        command = self.gen_command()
        return command


    def print_command_lines(self) -> None:
        print()
        for line in self.command_lines:
            for cmd_word in line:
                temp_str = ''
                if cmd_word.in_conditional:
                    temp_str += '[C]'
                if cmd_word.in_loop:
                    temp_str += '[L]'
                temp_str += cmd_word.text
                print(temp_str, end=' ')
            print()


    def print_command_words(self) -> None:
        print()
        print(f'{"word":60s}{"cond":>6}{"loop":>6}')
        for word in self.cmd_words:
            print(f'{word.text:60s}{word.in_conditional:6}{word.in_loop:6}')
        

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
        for cmd_word in self.cmd_words:
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


    def tokenify_command(self) -> None:
        cmd_tokens: list[Token] = []

        for word in self.cmd_words:
            token = self.get_best_token(word)
            cmd_tokens.append(token)

        self.cmd_tokens = cmd_tokens


    def expand_galaxy_tokens(self) -> None:
        """
        expands each individual token into a list of tokens
        most commonly will just be list with single item (the original token)
        sometimes will be multiple tokens

        reason is that some galaxy select or bool params hide flags or options as their possible values

        """
        out_tokens: list[Token] = []

        for token in self.cmd_tokens:
            expanded_tokens = []

            # attempt to expand if select or bool params
            if token.type == TokenTypes.GX_PARAM:
                param = token.value
                if type(param) == SelectParam:
                    expanded_tokens = self.expand_select_tokens(param, token.in_conditional)
                    print()
                elif type(param) == BoolParam:
                    expanded_tokens = self.expand_bool_tokens(param, token.in_conditional)
                    print()
            
            if len(expanded_tokens) > 0:
                out_tokens.append(expanded_tokens)
            else:
                out_tokens.append([token])
                        
        self.cmd_tokens = out_tokens


    def expand_select_tokens(self, param: SelectParam, in_conditional: bool) -> list[Token]:
        """
        NOTE does this work with key=$val where $val is gx param? 
        """
        expanded_tokens = []
        if self.should_expand_select(param):
            # expand into all possible tokens
            
            for opt in param.options:
                # EDGE CASE: <option value="-strand +"> into a kv_pair 
                str_list = opt.split(' ')
                if len(str_list) == 2 and str_list[0].startswith('-'):
                    new_token = Token(opt, TokenTypes.KV_PAIR)
                
                # normal scenarios. create temp cmd word and parse to token
                else:
                    temp_cmd_word = CommandWord(opt)
                    temp_cmd_word.in_conditional = in_conditional 
                    temp_cmd_word.expanded_text = [opt]
                    new_token = self.get_best_token(temp_cmd_word)
                
                expanded_tokens.append(new_token)

        return expanded_tokens


    def expand_bool_tokens(self, param: BoolParam, in_conditional: bool) -> list[Token]:
        expanded_tokens = []
        if self.should_expand_bool(param):
            # expand into all possible tokens
            pass
        return expanded_tokens


    def should_expand_select(self, param: SelectParam) -> bool:
        """
        check that each option is "" or starts with "-"
        """
        for opt in param.options:
            if not opt == "" and not opt.startswith('-'):
                return False
        return True


    def should_expand_bool(self, param: SelectParam) -> bool:
        """
        TODO HERE
        we expect a proper flag bool to have either 
        truevalue or falsevalue starting with '-' and the other == "" (None)
        should expand if both have value of any form
        """
        pass


    def gen_command(self) -> None:
        """
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
        while i < len(self.cmd_words) - 1:
            curr_word = self.cmd_words[i]
            next_word = self.cmd_words[i+1]
            curr_token = self.get_best_token(curr_word)
            next_token = self.get_best_token(next_word)

            # if kv pair, break and reassign curr/next tokens
            is_kv_pair = False
            delim = ' '
            if self.is_kv_pair(curr_token): 
                is_kv_pair = True
                curr_token, next_token, delim = self.split_keyval_to_best_tokens(curr_word)

            if self.is_linux_op(curr_token, next_token):
                command.update_positionals(positional_count, curr_token, is_after_options)                
                positional_count += 1

            elif self.is_flag(curr_token, next_token):
                is_after_options = True
                command.update_flags(curr_token)

            elif self.is_option(curr_token, next_token):
                is_after_options = True
                command.update_options(curr_token, next_token, delim)
                if not is_kv_pair:
                    i += 1

            else:
                # text positional
                # this has to happen last, as last resort
                # some examples of options which don't start with '-' exist. 
                command.update_positionals(positional_count, curr_token, is_after_options)                
                positional_count += 1

            i += 1
        return command



    def split_keyval_to_best_tokens(self, curr_word: CommandWord) -> Tuple[Token, Token, str]:
        """
        keyval options need to be split into two tokens
        """
        curr_word, next_word, delim = self.split_keyval_cmd(curr_word)

        curr_token = self.get_best_token(curr_word)
        next_token = self.get_best_token(next_word)

        return curr_token, next_token, delim


    def split_keyval_cmd(self, kv_cmd: str) -> list[str]:
        """
        handles the following patterns:
        --minid=$adv.min_dna_id
        --protein='off'
        ne=$ne
        etc
        """
        text = kv_cmd.expanded_text[0]
        possible_delims = ['=', ':', ' ']

        delim, delim_start, delim_end = self.get_first_unquoted(text, possible_delims)
        left_text, right_text = text[:delim_start], text[delim_end:]

        curr_word = CommandWord(left_text)
        curr_word.in_loop = kv_cmd.in_loop
        curr_word.in_conditional = kv_cmd.in_conditional
        curr_word.expanded_text = [left_text]
        
        next_word = CommandWord(right_text)
        next_word.in_loop = kv_cmd.in_loop
        next_word.in_conditional = kv_cmd.in_conditional
        next_word.expanded_text = [right_text]

        return curr_word, next_word, delim


    def get_first_unquoted(self, the_string: str, the_list: list[str]) -> Tuple[str, int]:
        """
        returns the first item in the_list found unquoted in the_string
        """
        hits = []

        # get locations of each item in the_list in the_string
        for item in the_list:
            item_start, item_end = find_unquoted(the_string, item)
            if item_start != -1:
                hits.append((item, item_start, item_end))

        # sort by pos ascending and return
        hits.sort(key=lambda x: x[1])
        return hits[0]


    def get_best_token(self, word: CommandWord) -> Token:
        # TODO situations with more than 1!
        if len(word.expanded_text) > 1:
            print('multiple expanded forms of cmd word')
            self.logger.log(2, 'multiple expanded forms of cmd word')
            sys.exit()

        # get best token representation of curr_word
        tokens = self.get_all_tokens(word.expanded_text[0])
        if len(tokens) == 0:
            print('could not resolve token')
            self.logger.log(2, 'could not resolve token')
            sys.exit()

        best_token = self.select_highest_priority_token(tokens)
        
        # transfer in_conditional status to token
        best_token.in_conditional = word.in_conditional

        return best_token


    def get_all_tokens(self, text: str) -> list[Token]:
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
            # just check if there is a gx_kw of same length 
            # gx_kws show up as kv_pairs too because of the ':'
            if len(gx_kws) > 0:
                return self.resolve_kvpair_and_gxkw_priority(kv_pairs + gx_kws)
            else:
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


    def resolve_kvpair_and_gxkw_priority(self, token_list: list[Token]) -> Token:
        longest_tokens = self.get_longest_token(token_list)
        
        # prioritise GX_KEYWORDs if they're in longest_tokens
        for token in longest_tokens:
            if token.type == TokenTypes.GX_KEYWORD:
                return token

        # otherwise just return first (will be KV_PAIR)
        return longest_tokens[0]


    def get_longest_token(self, token_list: list[Token]) -> list[Token]:
        """
        gets longest token in list
        returns multiple tokens if both have max len
        """   
        longest_text_len = max([len(t.value) for t in token_list])
        longest_tokens = [t for t in token_list if len(t.value) == longest_text_len]
        return longest_tokens


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
            default_val = param.get_default()
            
            if default_val is not None:
                # check if numbers first
                if len(get_quoted_numbers(default_val)) > 0:
                    return False
                elif len(get_raw_numbers(default_val)) > 0:
                    return False

                # then interpret as string
                elif default_val.startswith('-'):
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





