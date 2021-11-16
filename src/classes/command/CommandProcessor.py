

from typing import Tuple
import regex as re

from classes.command.Command import Command, Token, TokenType
from classes.params.ParamRegister import ParamRegister
from classes.outputs.OutputRegister import OutputRegister
from classes.Logger import Logger


from utils.regex_utils import find_unquoted


class CommandWord:
    def __init__(self, text: str, statement_block: int):
        self.text = text
        self.statement_block = statement_block
        self.in_loop = False
        self.in_conditional = False
        self.expanded_text: list[str] = []


class CommandProcessor:
    def __init__(self, lines: list[str], cmd_words: list[CommandWord], param_register: ParamRegister, out_register: OutputRegister, logger: Logger):
        """
        Command class receives the CommandLines
        """
        self.param_register = param_register
        self.out_register = out_register
        self.logger = logger
        self.lines = lines
        self.cmd_words = cmd_words
        self.env_vars: list[str] = []
        self.cmd_tokens: list[Token] = []


    def process(self) -> Command:
        self.standardise_cmd_words()
        #self.extract_env_vars()
        self.extract_aliases()
        self.expand_aliases()
        self.tokenify_command()
        command = self.gen_command()
        return command


    def print_command_words(self) -> None:
        print()
        print(f'{"word":60s}{"cond":>6}{"loop":>6}')
        for word in self.cmd_words:
            print(f'{word.text:60s}{word.in_conditional:6}{word.in_loop:6}')
        

    def pretty_print_tokens(self) -> None:
        print('tokens --------------')
        print(f'{"text":<20}{"gx_ref":20}{"type":25}{"in_cond":10}{"sblock":>5}')
        counter = 0
        for token_list in self.cmd_tokens:
            counter += 1
            for token in token_list:
                print(f'{counter:<3}{token}')


    def standardise_cmd_words(self) -> None:
        """
        env vars and aliases are already standardised to correct format.
        only cmd_words need to be addressed. 
        """
        for word in self.cmd_words:
            word.text = self.standardise_var_format(word.text)


    def standardise_var_format(self, text: str) -> str:
        """
        modifies cmd word to ensure the $var format is present, 
        rather than ${var}
        takes a safe approach using regex and resolving all vars one by one
        """
        matches = re.finditer(r'\$\{[\w.]+\}', text)
        matches = [[m[0], m.start(), m.end()] for m in matches]

        if len(matches) > 0:
            m = matches[0]
            # this is cursed but trust me it removes the 
            # curly braces for the match span
            text = text[:m[1] + 1] + text[m[1] + 2: m[2] - 1] + text[m[2] + 1:]
            text = self.standardise_var_format(text)

        return text    
                   

           


    # def extract_mv_aliases(self, line: str) -> list[Tuple[str, str]]:
    #     """
    #     mv ${output_dir}/summary.tab '$output_summary'
    #     mv '${ _aligned_root }.2${_aligned_ext}' '$output_aligned_reads_r'
    #     mv circos.svg ../
    #     mv circos.svg outputs/circos.svg

    #     mv input_file.tmp output${ ( $i + 1 ) % 2 }.tmp
        
    #     """
    #     if line.startswith('mv '):
    #         arg1, arg2 = line.split(' ')[-2:]

    #         # for ../ where we move the fileyntax where only FILE is given (no DEST)
    #         if arg1.startswith('-'):
    #             arg1 = arg2

    #         # set the source
    #         dest = self.get_source(arg1)
            
    #         # set the dest
    #         source = self.get_dest(arg2)

    #         #print(line)
    #         #print(f'{source} --> {dest}')
    #         if source is not None and dest is not None:
    #             self.aliases.add(source, dest, 'mv', line) 


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
            # if len(cmd_forms) == 0:
            #     print()
            cmd_word.expanded_text = cmd_forms


    def extract_env_vars(self) -> None:
        """
        export TERM=vt100
        export AUGUSTUS_CONFIG_PATH=`pwd`/augustus_dir/ &&
        export BCFTOOLS_PLUGINS=`which bcftools | sed 's,bin/bcftools,libexec/bcftools,'`;
        export MPLCONFIGDIR=\$TEMP &&
        export JAVA_OPTS="-Djava.awt.headless=true -Xmx\${GALAXY_MEMORY_MB:-1024}m"
        `pwd` -> set this as a known function? 

        Just ignoring this for now. not used anyway and possibly a little complex.
        """
        env_vars = []

        # for line in self.lines:
        #     if line.startswith('export '):
        #         left, right = self.split_variable_assignment(line)
        #         left = left[7:] # removes the 'export ' from line start

        #         # set the source
        #         source = self.get_source(left)
        #         dest = None # not even gonna worry about what it means. just marking as exists
            
        #         if source is not None:
        #             env_vars.append(source) 

        self.env_vars = env_vars


    def tokenify_command(self) -> None:
        cmd_tokens: list[Token] = []

        for word in self.cmd_words:
            # get initial token
            token = self.get_best_token(word, self.param_register, self.out_register)

            # possibly split token if GX_PARAM is hiding flags or options
            if token.type == TokenType.GX_PARAM:
                tokens = self.expand_galaxy_tokens(token)
            else:
                tokens = [token]

            cmd_tokens.append(tokens)

        self.cmd_tokens = cmd_tokens


    def expand_galaxy_tokens(self, token: Token) -> list[Token]:
        """
        expands each individual token into a list of tokens
        most commonly will just be list with single item (the original token)
        sometimes will be multiple tokens

        reason is that some galaxy select or bool params hide flags or options as their possible values

        every BoolParam will have 1+ 'realised_values'
        each SelectParam which is a list of flags / opts will have 1+ realised values

        """
        out_tokens: list[Token] = []

        values = self.param_register.get_realised_values(token.gx_ref)
        values = [v for v in values if v != '']

        if self.should_expand(values):
            for val in values:
                # in case its something like '-read_trkg yes'
                if val.startswith('-') and len(val.split(' ')) == 2:
                    new_token = Token(val, token.statement_block, TokenType.KV_PAIR)

                # else its a single word or a quoted phrase TODO CHECK THIS
                else:
                    new_word = self.init_cmd_word(val, token=token)
                    new_token = self.get_best_token(new_word, self.param_register, self.out_register)
                
                # transfer properties
                new_token.in_conditional = token.in_conditional
                new_token.in_loop = token.in_loop
                new_token.gx_ref = token.gx_ref
                out_tokens.append(new_token)
        else:
            out_tokens.append(token)
                        
        return out_tokens


    def should_expand(self, values: list[str]) -> bool:
        if len(values) == 0:
            return False

        elif all([v == '' for v in values]):
            return False
    
        for val in values:
            if not val == "" and not val.startswith('-'):
                return False

        return True


    def gen_command(self) -> None:
        """

        """
        command = Command()
        i = 0

        # iterate through command words (with next word for context)
        while i < len(self.cmd_tokens) - 1:
            curr_tokens = self.cmd_tokens[i]
            next_tokens = self.cmd_tokens[i+1]

            should_skip_next = False
            for ctoken in curr_tokens:

                # kv pair handling (edge case)
                if ctoken.type == TokenType.KV_PAIR: 
                    ctoken, ntoken, delim = self.split_keyval_to_best_tokens(ctoken)
                    command.update_options(ctoken, ntoken, delim=delim)
                    continue

                # everything else
                for ntoken in next_tokens:
                    skip_next = command.update(ctoken, ntoken, self.param_register, self.out_register)
                    if skip_next:
                        should_skip_next = True
            
            if should_skip_next:
                i += 2
            else:
                i += 1

        return command


    def split_keyval_to_best_tokens(self, kv_token: Token) -> Tuple[Token, Token, str]:
        """
        keyval options need to be split into two tokens
        """
        curr_word, next_word, delim = self.split_keyval_to_cmd_words(kv_token)

        curr_token = self.get_best_token(curr_word, self.param_register, self.out_register)
        next_token = self.get_best_token(next_word, self.param_register, self.out_register)

        if curr_token.gx_ref == '':
            curr_token.gx_ref = kv_token.gx_ref
        
        if next_token.gx_ref == '':
            next_token.gx_ref = kv_token.gx_ref

        return curr_token, next_token, delim


    def split_keyval_to_cmd_words(self, kv_token: Token) -> list[CommandWord]:
        """
        handles the following patterns:
        --minid=$adv.min_dna_id
        --protein='off'
        ne=$ne
        etc
        """
        text = kv_token.text
        possible_delims = ['=', ':', ' ']

        delim, delim_start, delim_end = self.get_first_unquoted(text, possible_delims)
        left_text, right_text = text[:delim_start], text[delim_end:]
       
        curr_word = self.init_cmd_word(left_text, token=kv_token)
        next_word = self.init_cmd_word(right_text, token=kv_token)

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


    


    


    





