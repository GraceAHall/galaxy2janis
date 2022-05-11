



from enum import Enum, auto
from typing import Optional
import regex as re

from xmltool.param.Param import Param

class TokenType(Enum):
    FUNCTION_CALL   = auto()
    GX_INPUT        = auto()
    GX_OUTPUT       = auto()
    GX_KW_DYNAMIC   = auto()
    GX_KW_STATIC    = auto()
    ENV_VAR         = auto()
    KV_PAIR         = auto()
    KV_LINKER       = auto()
    FORCED_PREFIX   = auto()
    BACKTICK_SHELL_STATEMENT = auto()
    QUOTED_STRING   = auto()
    QUOTED_NUM      = auto()
    RAW_STRING      = auto()
    RAW_NUM         = auto()
    LINUX_TEE       = auto()
    LINUX_REDIRECT  = auto()
    LINUX_STREAM_MERGE = auto()
    START_STATEMENT = auto()
    EXCISION        = auto()
    END_STATEMENT    = auto()
    EMPTY_STRING    = auto()
    UNKNOWN         = auto()


class Token:
    def __init__(self, match: re.Match[str], token_type: TokenType, gxparam: Optional[Param]=None):
        self.match = match
        self.type = token_type
        self.gxparam = gxparam
        
        self.position: Optional[int] = None
        self.in_conditional: bool = False
        self.in_loop: bool = False

    @property
    def text(self) -> str:
        return self.match[0] # type: ignore
    
    @property
    def start(self) -> int:
        return self.match.start()

    @property
    def end(self) -> int:
        return self.match.end()

    def __repr__(self) -> str:
        return f'Token: {self.text}, gxparam: {self.gxparam}'

