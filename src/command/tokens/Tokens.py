



from enum import Enum, auto
from typing import Optional
import regex as re

from tool.param.Param import Param

class TokenType(Enum):
    GX_INPUT        = auto()
    GX_OUTPUT       = auto()
    GX_KEYWORD      = auto()
    ENV_VAR         = auto()
    KV_PAIR         = auto()
    QUOTED_STRING   = auto()
    QUOTED_NUM      = auto()
    RAW_STRING      = auto()
    RAW_NUM         = auto()
    LINUX_TEE       = auto()
    LINUX_REDIRECT  = auto()
    LINUX_STREAM_MERGE = auto()
    START_STATEMENT = auto()
    END_STATEMENT   = auto()
    UNKNOWN         = auto()


class Token:
    def __init__(self, match: re.Match[str], token_type: TokenType, gxvar: Optional[Param]=None):
        self.match = match
        self.type = token_type
        self.gxvar = gxvar
        
    @property
    def text(self) -> str:
        return self.match[0] # type: ignore
    
    @property
    def start(self) -> int:
        return self.match.start()

    @property
    def end(self) -> int:
        return self.match.end()


    """
    def __str__(self) -> str:
        return f'{self.text[:29]:<30}{self.gx_ref[:29]:30}{self.type.name:25}{self.in_conditional:5}'
    """



