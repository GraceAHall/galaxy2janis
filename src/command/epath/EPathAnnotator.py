








from abc import ABC, abstractmethod
from typing import Iterable, Optional, Tuple
from command.epath.ExecutionPath import ExecutionPath
from command.tokens.Tokens import Token


class EPathAnnotator(ABC):
    """
    iterates through a ExecutionPath, yielding the current tokens being assessed.
    keeps track of the location we are in the ExecutionPath

    ingests ExecutionPaths and extracts tool components from the epath's tokens
    Example ExecutionPath (as tokens):
    abricate $sample_name --no-header --minid = 80 --db = card > $report
    """

    @abstractmethod
    def iter(self, epath: ExecutionPath) -> Iterable[Tuple[Token, list[Token]]]:
        """
        iterates through the ExecutionPath's tokens
        yields the current token, followed by trailing tokens which are
        related to the current token, if the current token seems like an option 
        (--prefix and val(s))
        """
        ...
    
    @abstractmethod
    def search(self, epath: ExecutionPath) -> Optional[Tuple[Token, list[Token]]]:
        """
        searches for text within the epath.
        if found, will return the corresponding token and trailing tokens if related.
        will excise these from the epath
        """
        ...