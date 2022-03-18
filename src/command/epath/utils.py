


from command.components.Flag import Flag
from command.components.Option import Option
from command.tokens.Tokens import Token, TokenType
from xmltool.param.InputParam import BoolParam, SelectParam


NON_VALUE_TOKENTYPES = set([
    TokenType.LINUX_TEE, 
    TokenType.LINUX_REDIRECT,
    TokenType.LINUX_STREAM_MERGE,
    TokenType.END_SENTINEL,
    TokenType.EXCISION,
])

def is_bool_select(token: Token) -> bool:
    if token.type == TokenType.GX_INPUT:
        match token.gxvar:
            case BoolParam() | SelectParam():
                return True
            case _:
                pass
    return False

def is_flag(ctoken: Token, ntoken: Token) -> bool:
    if looks_like_a_flag(ctoken):
        if ntoken.type in NON_VALUE_TOKENTYPES:
            return True
        elif looks_like_a_flag(ntoken):
            return True
    return False

def looks_like_a_flag(token: Token) -> bool:
    if token.type == TokenType.FORCED_PREFIX:
        return True
    if token.type == TokenType.RAW_STRING and token.text.startswith('-'):
        return True
    return False

def is_option(ctoken: Token, ntoken: Token) -> bool:
    """
    happens 2nd after 'is_flag()'
    already know that its not a flag, so if the current token
    looks like a flag/option, it has to be an option. 
    """
    if ntoken.type == TokenType.KV_LINKER:
        return True 
    elif not is_flag(ctoken, ntoken):
        if looks_like_a_flag(ctoken) and is_positional(ntoken):
            return True
    return False

def is_positional(token: Token) -> bool:
    if not looks_like_a_flag(token):
        if token.type not in NON_VALUE_TOKENTYPES:
            return True
    return False

def cast_opt_to_flag(option: Option) -> Flag:
    return Flag(
        prefix=option.prefix,
        gxvar=option.gxvar,
        stage=option.stage,
        presence_array=option.presence_array
    )
