

from command.components.Positional import Positional
from command.components.Flag import Flag
from command.components.Option import Option
from command.components.linux_constructs import Redirect
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
    cmd_pos=0, 
    before_opts=True, 
    gxvar=None, 
    presence_array=[True, True, True]
)
MOCK_POSIT1.value_record = MOCK_VALUERECORD_POSIT1

MOCK_POSIT2 = Positional(
    value='$sample_name', 
    epath_id=0, 
    cmd_pos=1, 
    before_opts=True, 
    gxvar=None, 
    presence_array=[True, True, True]
)
MOCK_POSIT2.value_record = MOCK_VALUERECORD_POSIT2

MOCK_FLAG1 = Flag(
    prefix='--noheader', 
    cmd_pos=2, 
    gxvar=MOCK_BOOLPARAM1, 
    stage='pre_options', 
    presence_array=[True, False, True]
)

MOCK_OPTION1 = Option(
    prefix='--minid', 
    values=['$adv.min_dna_id'], 
    epath_id=0, 
    delim='=', 
    cmd_pos=2, 
    gxvar=MOCK_FLOATPARAM1, 
    presence_array=[True, True, True]
)
MOCK_OPTION1.value_record = MOCK_VALUERECORD_OPT1

MOCK_OPTION2 = Option(
    prefix='--mincov', 
    values=['$adv.min_cov'], 
    epath_id=0, 
    delim='=', 
    cmd_pos=2, 
    gxvar=MOCK_FLOATPARAM2, 
    presence_array=[True, True, True]
)
MOCK_OPTION2.value_record = MOCK_VALUERECORD_OPT2

MOCK_OPTION3 = Option(
    prefix='--db', 
    values=['card'], 
    epath_id=0, 
    delim='=', 
    cmd_pos=2, 
    gxvar=MOCK_SELECTPARAM1, 
    presence_array=[True, True, True]
)
MOCK_OPTION3.value_record = MOCK_VALUERECORD_OPT3


from command.regex.scanners import get_all

redirect_matches = get_all('>')
redirect_token = Token(redirect_matches[0], TokenType.LINUX_REDIRECT)
file_matches = get_all('>')
file_token = Token(file_matches[0], TokenType.GX_OUTPUT)
MOCK_REDIRECT1 = Redirect(redirect_token, file_token)
MOCK_REDIRECT1.gxvar = MOCK_OUTPARAM1


