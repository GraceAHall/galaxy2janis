


from command.tokens.Tokens import Token, TokenType
from tool.param.InputParam import BoolParam, SelectParam


NON_VALUE_TOKENTYPES = set([
    TokenType.LINUX_TEE, 
    TokenType.LINUX_REDIRECT,
    TokenType.LINUX_STREAM_MERGE,
    TokenType.END_SENTINEL,
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
        if looks_like_a_flag(ntoken):
            return True
        elif ntoken.type in NON_VALUE_TOKENTYPES:
            return True
    return False

def looks_like_a_flag(token: Token) -> bool:
    if token.type == TokenType.RAW_STRING and token.text.startswith('-'):
        return True
    return False

def is_option(ctoken: Token, ntoken: Token) -> bool:
    """
    happens 2nd after 'is_flag()'
    already know that its not a flag, so if the current token
    looks like a flag/option, it has to be an option. 
    """
    if looks_like_a_flag(ctoken):
        return True
    return False