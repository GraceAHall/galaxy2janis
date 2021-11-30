


from enum import Enum


class TokenType(Enum):
    GX_PARAM        = 0
    GX_OUT          = 1
    QUOTED_STRING   = 2
    RAW_STRING      = 3
    QUOTED_NUM      = 4
    RAW_NUM         = 5
    LINUX_OP        = 6
    GX_KEYWORD      = 7
    KV_PAIR         = 8
    END_COMMAND     = 9



class Token:
    def __init__(self, text: str, token_type: TokenType):
        self.text = text
        self.type = token_type
        self.in_conditional = False
        self.in_loop = False
        self.gx_ref: str = text if token_type in [TokenType.GX_PARAM, TokenType.GX_OUT] else ''
        

    def __str__(self) -> str:
        return f'{self.text[:29]:<30}{self.gx_ref[:29]:30}{self.type.name:25}{self.in_conditional:5}'



