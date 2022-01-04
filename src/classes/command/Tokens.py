


from enum import Enum, auto


class TokenType(Enum):
    GX_PARAM        = auto()
    GX_OUT          = auto()
    QUOTED_STRING   = auto()
    RAW_STRING      = auto()
    QUOTED_NUM      = auto()
    RAW_NUM         = auto()
    LINUX_OP        = auto()
    GX_KEYWORD      = auto()
    KV_PAIR         = auto()
    END_COMMAND     = auto()



class Token:
    def __init__(self, text: str, token_type: TokenType):
        self.text = text
        self.type = token_type
        self.in_conditional = False
        self.in_loop = False
        self.gx_ref: str = text if token_type in [TokenType.GX_PARAM, TokenType.GX_OUT] else ''
        

    def __str__(self) -> str:
        return f'{self.text[:29]:<30}{self.gx_ref[:29]:30}{self.type.name:25}{self.in_conditional:5}'



