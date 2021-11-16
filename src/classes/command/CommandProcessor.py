

from collections import defaultdict
from typing import Tuple
import regex as re

from classes.command.Alias import AliasRegister
from classes.command.Command import Command, Token, TokenType
from classes.command.CommandWord  import CommandWord
from classes.params.ParamRegister import ParamRegister
from classes.outputs.OutputRegister import OutputRegister
from classes.Logger import Logger

from utils.regex_utils import find_unquoted
from utils.command_utils import get_best_token, init_cmd_word


class CommandProcessor:
    def __init__(self, command_words: dict[int, list[CommandWord]], param_register: ParamRegister, out_register: OutputRegister, alias_register: AliasRegister, logger: Logger):
        """
        Command class receives the CommandLines
        """
        self.command_words = command_words
        self.command_tokens: dict[int, list[list[Token]]] = {}
        self.param_register = param_register
        self.out_register = out_register
        self.alias_register = alias_register
        self.logger = logger

        # TODO include the following
        # or maybe not? 
        # self.main_requirement = main_requirement


    def process(self) -> Command:
        for statement_block, cmd_words in self.command_words.items():
            cmd_words = self.expand_aliases(cmd_words)
            cmd_tokens = self.tokenify_cmd_words(cmd_words)
            self.command_tokens[statement_block] = cmd_tokens
        
        best_block = self.get_best_statement_block()
        self.command = self.gen_command(best_block)


    def expand_aliases(self, cmd_words: list[CommandWord]) -> list[CommandWord]:
        # is this the way to go? 
        # not sure about expanded text rip
        for word in cmd_words:
            word.expanded_text = self.alias_register.template(word.text)
            
        return cmd_words


    def tokenify_cmd_words(self, cmd_words: list[CommandWord]) -> list[CommandWord]:
        cmd_tokens: list[Token] = []

        for word in cmd_words:
            # get initial token
            token = get_best_token(word, self.param_register, self.out_register)

            # possibly split token if GX_PARAM is hiding flags or options
            if token.type == TokenType.GX_PARAM:
                tokens = self.expand_galaxy_tokens(token)
                print()
            else:
                tokens = [token]

            cmd_tokens.append(tokens)

        return cmd_tokens


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
                    new_word = init_cmd_word(val, token=token)
                    new_token = get_best_token(new_word, self.param_register, self.out_register)
                
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


    def get_best_statement_block(self) -> list[list[Token]]:
        """
        just counts the number of galaxy objects and kvpairs which
        appear in each block. simple for now. 
        """
        # single command block
        if len(self.command_tokens) == 1:
            return self.command_tokens[0]

        # multiple command blocks
        # tally num gx objs per block
        # now thats nested!
        block_scores_dict = defaultdict(int)
        for statement_block, cmd_tokens in self.command_tokens.items():
            for line_tokens in cmd_tokens:
                for token in line_tokens:
                    if token.type in [TokenType.GX_OUT, TokenType.GX_PARAM, TokenType.KV_PAIR]:
                        block_scores_dict[statement_block] += 1

        # sort by tally and return best
        block_scores = list(block_scores_dict.items())
        block_scores.sort(key=lambda x: x[1], reverse=True)
        best_block = block_scores[0][0]

        return self.command_tokens[best_block]


    def gen_command(self, command_tokens: list[Token]) -> Command:
        """
        goes through the tokens to work out command structure
        looks ahead to resolve difference between flag and opt with arg etc

        """
        command = Command()
        i = 0

        # iterate through command words (with next word for context)
        while i < len(command_tokens) - 1:
            curr_tokens = command_tokens[i]
            next_tokens = command_tokens[i+1]

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

        curr_token = get_best_token(curr_word, self.param_register, self.out_register)
        next_token = get_best_token(next_word, self.param_register, self.out_register)

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
       
        curr_word = init_cmd_word(left_text, token=kv_token)
        next_word = init_cmd_word(right_text, token=kv_token)

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


    def print_command_words(self) -> None:
        print()
        print(f'{"word":60s}{"cond":>6}{"loop":>6}')
        for word in self.cmd_words:
            print(f'{word.text:60s}{word.in_conditional:6}{word.in_loop:6}')
        
    
    # deprecated
    def pretty_print_tokens(self) -> None:
        print('tokens --------------')
        print(f'{"text":<20}{"gx_ref":20}{"type":25}{"in_cond":10}{"sblock":>5}')
        counter = 0
        for token_list in self.cmd_tokens:
            counter += 1
            for token in token_list:
                print(f'{counter:<3}{token}')

    


    





