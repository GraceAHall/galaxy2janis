


from .Token import Token, TokenType
from ..regex import scanners as scanners


def spawn_end_sentinel() -> Token:
    matches = scanners.get_all('end')
    return Token(matches[0], TokenType.END_STATEMENT)

def spawn_kv_linker(delim: str) -> Token:
    matches = scanners.get_all(delim)
    return Token(matches[0], TokenType.KV_LINKER)

def spawn_function_call() -> Token:
    matches = scanners.get_all('__FUNCTION_CALL__')
    return Token(matches[0], TokenType.FUNCTION_CALL)
    
def spawn_backtick_section() -> Token:
    matches = scanners.get_all('__BACKTICK_SHELL_STATEMENT__')
    return Token(matches[0], TokenType.BACKTICK_SHELL_STATEMENT)

