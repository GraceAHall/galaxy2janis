
# pyright: basic

from typing import Tuple

from command.tokens.Tokens import Token, TokenType
from tool.param.OutputRegister import OutputRegister
from tool.param.ParamRegister import ParamRegister 
from command.regex.utils import (

    find_unquoted
)  





def split_keyval_to_best_tokens(kv_token: Token, param_register: ParamRegister, out_register: OutputRegister) -> Tuple[Token, Token, str]:
    """
    keyval options need to be split into two tokens
    """
    curr_word, next_word, delim = split_keyval_to_text(kv_token)

    curr_token = tokenify(curr_word, param_register=param_register, out_register=out_register)
    curr_token = transfer_token_attributes(kv_token, curr_token)
        
    next_token = tokenify(next_word, param_register=param_register, out_register=out_register)
    next_token = transfer_token_attributes(kv_token, next_token)

    return curr_token, next_token, delim


def split_keyval_to_text(kv_token: Token) -> list[str]:
    """
    handles the following patterns:
    --minid=$adv.min_dna_id
    --protein='off'
    ne=$ne
    etc
    """
    text = kv_token.text
    possible_delims = ['=', ':', ' ']

    delim, delim_start, delim_end = get_first_unquoted(text, possible_delims)
    left_text, right_text = text[:delim_start], text[delim_end:]

    return left_text, right_text, delim


def tokenify(word: str, param_register: ParamRegister=None, out_register: OutputRegister=None, prioritise_tokens: bool=True) -> Token:
    """
    generates a token from word. 
    where multiple token types are possible, selects the most appropriate. 
    """
    temp_tokens = get_all_tokens(word, param_register=param_register, out_register=out_register)
    best_token = select_highest_priority_token(temp_tokens, prioritise_tokens)
    return best_token


def get_all_tokens(the_string: str, param_register: ParamRegister=None, out_register: OutputRegister=None) -> list[Token]:
    """
    gets all the possible token interpretations of the_string
    """  
    # early exits
    if the_string == '__END_STATEMENT__':
        return [Token('', TokenType.END_STATEMENT)]
    elif the_string == '':
        raise Exception('cannot tokenify blank string')

    tokens = []

    # galaxy inputs / outputs
    # quoted or not doesn't matter. just linking. can resolve its datatype later. 
    ch_vars = get_variables(the_string) # get cheetah vars
    if param_register is not None:
        gx_params = [x for x in ch_vars if param_register.get(x)[0] is not None]
        tokens += [Token(gx_var, TokenType.GX_INPUT) for gx_var in gx_params]
    
    if out_register is not None:
        gx_outs = [x for x in ch_vars if out_register.get(x) is not None]  
        tokens += [Token(out, TokenType.GX_OUTPUT) for out in gx_outs]  

    # quoted numbers / strings
    quoted_num_lits = get_quoted_numbers(the_string)
    quoted_num_lits = [m.strip('\'"') for m in quoted_num_lits]
    tokens += [Token(m, TokenType.QUOTED_NUM) for m in quoted_num_lits]

    quoted_str_lits = get_quoted_strings(the_string)
    quoted_str_lits = [m.strip('\'"') for m in quoted_str_lits]
    tokens += [Token(m, TokenType.QUOTED_STRING) for m in quoted_str_lits]
    
    # raw numbers / strings
    raw_num_lits = get_raw_numbers(the_string)
    tokens += [Token(m, TokenType.RAW_NUM) for m in raw_num_lits]
    
    raw_str_lits = get_raw_strings(the_string)
    tokens += [Token(m, TokenType.RAW_STRING) for m in raw_str_lits]
    
    # TODO this is pretty weak. actually want to search for 
    # unquoted operator in word. split if necessary. 
    linux_operators = get_linux_operators(the_string)
    tokens += [Token(op, TokenType.LINUX_OP) for op in linux_operators]

    kv_pairs = get_keyval_pairs(the_string)
    tokens += [Token(kv, TokenType.KV_PAIR) for kv in kv_pairs]

    # fallback
    if len(tokens) == 0:
        tokens += [Token(the_string, TokenType.RAW_STRING)]

    return tokens


def select_highest_priority_token(tokens: list[Token], prioritise_tokens: True) -> Token:
    # extremely simple. just the token with longest text match.
    # solves issues of galaxy param being embedded in string. 
    if prioritise_tokens:
        return get_highest_priority_token(tokens)
    else:
        return get_longest_token(tokens)
    

def get_highest_priority_token(tokens: list[Token]) -> Token:
    kv_pairs = [t for t in tokens if t.type == TokenType.KV_PAIR]
    gx_params = [t for t in tokens if t.type == TokenType.GX_INPUT]
    gx_outs = [t for t in tokens if t.type == TokenType.GX_OUTPUT]
    linux_ops = [t for t in tokens if t.type == TokenType.LINUX_OP]

    if len(kv_pairs) > 0:
        return kv_pairs[0]
    elif len(gx_params) > 0:
        return gx_params[0]
    elif len(gx_outs) > 0:
        return gx_outs[0]
    elif len(linux_ops) > 0:
        return linux_ops[0]
            
    return tokens[0]


def get_longest_token(token_list: list[Token]) -> list[Token]:
    """
    gets longest token in list
    returns multiple tokens if both have max len
    """   
    longest_text_len = max([len(t.text) for t in token_list])
    tokens = [t for t in token_list if len(t.text) == longest_text_len]
    
    if len(tokens) > 1:
        return get_highest_priority_token(tokens)
    else:
        return tokens[0]


def get_first_unquoted(the_string: str, the_list: list[str]) -> Tuple[str, int]:
    """
    returns the first item in the_list found unquoted in the_string
    """
    hits = []
    # workaround for when entire string is quoted
    if the_string[0] in ['"', "'"] and the_string[-1] in ['"', "'"]:
        the_string = '_' + the_string[1:-1] + '_'

    # get locations of each item in the_list in the_string
    for item in the_list:
        item_start, item_end = find_unquoted(the_string, item)
        if item_start != -1:
            hits.append((item, item_start, item_end))

    # sort by pos ascending and return
    hits.sort(key=lambda x: x[1])
    return hits[0]


def transfer_token_attributes(source_token: Token, dest_token: Token) -> Token:
    dest_token.in_conditional = source_token.in_conditional
    dest_token.in_loop = source_token.in_loop

    if dest_token.gx_ref == '':
        dest_token.gx_ref = source_token.gx_ref
    
    return dest_token


def split_line_by_ands(line: str) -> str:
    out_lines = []
    active_line = ''
    words = line.split(' ')

    for word in words:
        if word in ['&&', ';']:
            out_lines.append(active_line)
            active_line = ''
        else:
            active_line += ' ' + word
    
    out_lines.append(active_line)
    out_lines = [ln.strip() for ln in out_lines]
    out_lines = [ln for ln in out_lines if ln != '']
    return out_lines


