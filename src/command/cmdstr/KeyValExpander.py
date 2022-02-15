
from command.cmdstr.ConstructTracker import ConstructTracker
from command.tokens.Tokens import Token, TokenType
from command.tokens.Tokenifier import Tokenifier
from command.cmdstr.utils import (
    split_lines, 
    split_words, 
    join_lines
)

class KeyValExpander:
    def __init__(self, tokenifier: Tokenifier):
        self.construct_tracker = ConstructTracker()
        self.tokenifier = tokenifier

    def expand(self, the_string: str) -> str:
        expanded_lines: list[str] = []
        # expand each line (returns original line if no kv pairs)
        for line in split_lines(the_string):
            expanded_lines.append(self.expand_line(line))
        return join_lines(expanded_lines)

    def expand_line(self, line: str) -> str:
        # expand each line (returns original line if no kv pairs)
        if self.construct_tracker.should_kvexpand_line(line):
            words = split_words(line)
            tokens = [self.tokenifier.tokenify(word) for word in words]
            expanded_words = [self.expand_token_to_str(token) for token in tokens]
            return ' '.join(expanded_words)
        return line

    def expand_token_to_str(self, token: Token) -> str:
        if token.type == TokenType.KV_PAIR:
            return str(token.match.group(1)) + ' ' + str(token.match.group(2))
        else:
            return(token.match.string)