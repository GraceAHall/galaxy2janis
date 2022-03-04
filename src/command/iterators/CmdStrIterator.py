








from abc import ABC, abstractmethod
from typing import Iterable, Tuple
from command.cmdstr.ToolExecutionSource import ToolExecutionSource
from command.tokens.Tokens import Token


class CmdStrIterator(ABC):
    """
    iterates through a ToolExecutionSource, yielding the current tokens being assessed.
    keeps track of the location we are in the ToolExecutionSource

    ingests ToolExecutionSources and extracts tool components 
    from these strings. 
    
    Example ToolExecutionSource:
    abricate $sample_name --no-header --minid=80 --db=card > $report

    ideally, our CmdStrIterator would identify the following:
    pos1:   abricate
    pos2:   $sample_name
    flag1:  --no-header
    opt1:   --minid, 80
    opt2:   --db, card

    the '> $report' would already have been identified as file Stdout to $report and removed, so wouldn't actually appear in the ToolExecutionSource.
    """

    @abstractmethod
    def iter(self, cmdstr: ToolExecutionSource) -> Iterable[Tuple[Token, list[Token]]]:
        ...