


from command.tokens.Tokens import Token, TokenType
from command.regex import scanners as scanners


def spawn_end_sentinel() -> Token:
    matches = scanners.get_all('end')
    return Token(matches[0], TokenType.END_STATEMENT)

def spawn_kv_linker(delim: str) -> Token:
    matches = scanners.get_all(delim)
    return Token(matches[0], TokenType.KV_LINKER)