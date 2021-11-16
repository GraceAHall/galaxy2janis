



from classes.command.Command import Token, TokenType
from classes.command.CommandWord  import CommandWord
from classes.outputs.OutputRegister import OutputRegister
from classes.params.ParamRegister import ParamRegister
from utils.regex_utils import (
    get_cheetah_vars, 
    get_quoted_numbers,
    get_raw_numbers,
    get_quoted_strings,
    get_raw_strings,
    get_linux_operators,
    get_keyval_pairs
)


def remove_ands_from_line(line: str) -> str:
    line_elems = line.split(' ')
    line_elems = [e for e in line_elems if e != '&&' and e != ';']
    line_elems = [e for e in line_elems if e != '']
    return ' '.join(line_elems)


def init_cmd_word(text: str, token=None) -> CommandWord:
    new_word = CommandWord(text, -1)
    new_word.expanded_text = [text]

    # if token give, pass its attributes to the cmd word
    if token:
        new_word.in_conditional = token.in_conditional
        new_word.in_loop = token.in_loop
        new_word.statement_block = token.statement_block

    return new_word


def get_best_token(word: CommandWord, param_register: ParamRegister, out_register: OutputRegister) -> Token:
    tokens = []
    
    if len(word.expanded_text) > 1:
        print()

    # get best-fit token for each form of curr_word 
    for text in word.expanded_text:
        temp_tokens = get_all_tokens(text, word.statement_block, param_register, out_register)
        
        best_token = select_highest_priority_token(temp_tokens)
        tokens.append(best_token)

    # from the best-fit tokens, choose the final best fit
    final_token = select_highest_priority_token(tokens)

    # transfer in_conditional status to token
    final_token.in_conditional = word.in_conditional    

    return final_token


def get_all_tokens(text: str, statement_block: int, param_register: ParamRegister, out_register: OutputRegister) -> list[Token]:
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
        return [Token('', statement_block, TokenType.END_COMMAND)]

    # find quoted numbers and strings. quotes are removed
    quoted_num_lits = get_quoted_numbers(text)
    quoted_num_lits = [m.strip('\'"') for m in quoted_num_lits]
    tokens += [Token(m, statement_block, TokenType.QUOTED_NUM) for m in quoted_num_lits]

    quoted_str_lits = get_quoted_strings(text)
    quoted_str_lits = [m.strip('\'"') for m in quoted_str_lits]
    tokens += [Token(m, statement_block, TokenType.QUOTED_STRING) for m in quoted_str_lits]
    
    raw_num_lits = get_raw_numbers(text)
    tokens += [Token(m, statement_block, TokenType.RAW_NUM) for m in raw_num_lits]
    
    raw_str_lits = get_raw_strings(text)
    tokens += [Token(m, statement_block, TokenType.RAW_STRING) for m in raw_str_lits]
    
    # galaxy inputs
    # quoted or not doesn't matter. just linking. can resolve its datatype later. 
    ch_vars = get_cheetah_vars(text)
    gx_params = [x for x in ch_vars if param_register.get(x) is not None]
    tokens += [Token(gx_var, statement_block, TokenType.GX_PARAM) for gx_var in gx_params]
    
    # galaxy 
    ch_vars = get_cheetah_vars(text) # get cheetah vars
    gx_out = [x for x in ch_vars if out_register.get(x) is not None]  # subsets to galaxy out vars
    tokens += [Token(out, statement_block, TokenType.GX_OUT) for out in gx_out]  # transform to tokens

    # TODO this is pretty weak. actually want to search for 
    # unquoted operator in word. split if necessary. 
    linux_operators = get_linux_operators(text)
    tokens += [Token(op, statement_block, TokenType.LINUX_OP) for op in linux_operators]

    kv_pairs = get_keyval_pairs(text)
    tokens += [Token(kv, statement_block, TokenType.KV_PAIR) for kv in kv_pairs]

    # fallback
    if len(tokens) == 0:
        tokens += [Token(text, statement_block, TokenType.RAW_STRING)]

    return tokens


def select_highest_priority_token(tokens: list[Token]) -> Token:
    # extremely simple. just the token with longest text match.
    # solves issues of galaxy param being embedded in string. 
    
    kv_pairs = [t for t in tokens if t.type == TokenType.KV_PAIR]
    gx_params = [t for t in tokens if t.type == TokenType.GX_PARAM]
    gx_outs = [t for t in tokens if t.type == TokenType.GX_OUT]
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
    longest_tokens = [t for t in token_list if len(t.text) == longest_text_len]
    return longest_tokens