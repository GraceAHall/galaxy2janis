

from gx.command.components import Positional
from gx.command.components import Flag
from gx.command.components import Option
from gx.command.components import RedirectOutput
#from gx.command.components import InputOutput
#from gx.command.components import WildcardOutput


from .mock_params import MOCK_DATAPARAM1
from .mock_params import MOCK_BOOLPARAM1
from .mock_params import MOCK_FLOATPARAM1
from .mock_params import MOCK_SELECTPARAM1
from .mock_params import MOCK_OUTPARAM1

from .mock_params import (
    MOCK_BOOLPARAM1,
    MOCK_SELECTPARAM1,
    MOCK_FLOATPARAM1,
    MOCK_OUTPARAM1
)

MOCK_POSIT1 = Positional()
MOCK_POSIT1.gxparam = MOCK_DATAPARAM1
MOCK_POSIT1.values.add('$in.infastq')
MOCK_POSIT1.cmd_pos = 0
MOCK_POSIT1.before_opts = True

MOCK_POSIT2 = Positional()
MOCK_POSIT2.values.add('abricate')
MOCK_POSIT2.cmd_pos = 0
MOCK_POSIT2.before_opts = True

MOCK_POSIT3 = Positional()
MOCK_POSIT3.values.add('$sample_name')
MOCK_POSIT3.cmd_pos = 1
MOCK_POSIT3.before_opts = True

MOCK_FLAG1 = Flag(prefix='--noheader')
MOCK_FLAG1.cmd_pos = 2
MOCK_FLAG1.gxparam = MOCK_BOOLPARAM1

MOCK_OPTION1 = Option('--minid')
MOCK_OPTION1.values.add('$adv.min_dna_id')
MOCK_OPTION1.delim = '='
MOCK_OPTION1.cmd_pos = 2
MOCK_OPTION1.gxparam = MOCK_FLOATPARAM1

MOCK_OPTION2 = Option('--db')
MOCK_OPTION2.values.add('card')
MOCK_OPTION2.delim = '='
MOCK_OPTION2.cmd_pos = 2
MOCK_OPTION2.gxparam = MOCK_SELECTPARAM1

MOCK_REDIRECT1 = RedirectOutput('>', 'report.txt')
MOCK_REDIRECT1.gxparam = MOCK_OUTPARAM1


