

from command.Command import Command


from .mock_commandstring import MOCK_CMDSTR1
from .mock_commandcomponents import (
    MOCK_POSIT1,
    MOCK_POSIT2,
    MOCK_FLAG1,
    MOCK_OPTION1, 
    MOCK_OPTION2, 
    MOCK_OPTION3,
    MOCK_REDIRECT1
)

MOCK_COMMAND = Command(MOCK_CMDSTR1)
MOCK_COMMAND.positionals = {
    0: MOCK_POSIT1,
    1: MOCK_POSIT2
}
MOCK_COMMAND.flags = {
    '--noheader': MOCK_FLAG1
}
MOCK_COMMAND.options = {
    '--minid': MOCK_OPTION1,
    '--mincov': MOCK_OPTION2,
    '--db': MOCK_OPTION3
}
MOCK_COMMAND.redirect = MOCK_REDIRECT1

