

from command.components.inputs import Positional, Flag, Option
from command.components.outputs import RedirectOutput
from command.tokens.Tokens import Token, TokenType
from .mock_valuerecord import (
    MOCK_VALUERECORD_POSIT1,
    MOCK_VALUERECORD_POSIT2,
    MOCK_VALUERECORD_OPT1,
    MOCK_VALUERECORD_OPT2,
    MOCK_VALUERECORD_OPT3
)

from .mock_params import (
    MOCK_BOOLPARAM1,
    MOCK_SELECTPARAM1,
    MOCK_FLOATPARAM1,
    MOCK_FLOATPARAM2,
    MOCK_OUTPARAM1
)

MOCK_POSIT1 = Positional(
    value='abricate', 
    epath_id=0, 
)
MOCK_POSIT1.cmd_pos = 0
MOCK_POSIT1.before_opts = True
MOCK_POSIT1.presence_array = [True, True, True]
MOCK_POSIT1.value_record = MOCK_VALUERECORD_POSIT1

MOCK_POSIT2 = Positional(
    value='$sample_name', 
    epath_id=0, 
)
MOCK_POSIT2.cmd_pos = 1
MOCK_POSIT2.before_opts = True
MOCK_POSIT2.presence_array = [True, True, True]
MOCK_POSIT2.value_record = MOCK_VALUERECORD_POSIT2

MOCK_FLAG1 = Flag(prefix='--noheader')
MOCK_FLAG1.cmd_pos = 2
MOCK_FLAG1.gxparam = MOCK_BOOLPARAM1
MOCK_FLAG1.presence_array = [True, True, True]

MOCK_OPTION1 = Option(
    prefix='--minid', 
    values=['$adv.min_dna_id'], 
    epath_id=0, 
    delim='=', 
)
MOCK_OPTION1.cmd_pos = 2
MOCK_OPTION1.gxparam = MOCK_FLOATPARAM1
MOCK_OPTION1.presence_array = [True, True, True]
MOCK_OPTION1.value_record = MOCK_VALUERECORD_OPT1

MOCK_OPTION2 = Option(
    prefix='--mincov', 
    values=['$adv.min_cov'], 
    epath_id=0, 
    delim='=', 
)
MOCK_OPTION2.cmd_pos = 2
MOCK_OPTION2.gxparam = MOCK_FLOATPARAM2
MOCK_OPTION2.presence_array = [True, True, True]
MOCK_OPTION2.value_record = MOCK_VALUERECORD_OPT2

MOCK_OPTION3 = Option(
    prefix='--db', 
    values=['card'], 
    epath_id=0, 
    delim='=', 
)
MOCK_OPTION3.cmd_pos = 2
MOCK_OPTION3.gxparam = MOCK_SELECTPARAM1
MOCK_OPTION3.presence_array = [True, True, True]
MOCK_OPTION3.value_record = MOCK_VALUERECORD_OPT3


from command.regex.scanners import get_all

redirect_matches = get_all('>')
redirect_token = Token(redirect_matches[0], TokenType.LINUX_REDIRECT)
file_matches = get_all('>')
file_token = Token(file_matches[0], TokenType.GX_OUTPUT)
MOCK_REDIRECT1 = RedirectOutput((redirect_token, file_token))
MOCK_REDIRECT1.gxparam = MOCK_OUTPARAM1


