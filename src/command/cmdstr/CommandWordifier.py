

from command.cmdstr.ConstructTracker import ConstructTracker
from command.cmdstr.utils import split_lines, split_words
from command.tokens.Tokenifier import Tokenifier
from command.cmdstr.CommandWord import CommandWord
from command.cmdstr.CommandWord import CommandWordFactory


class CommandWordifier:
    def __init__(self, tokenifier: Tokenifier):
        self.tracker = ConstructTracker()
        self.factory = CommandWordFactory(tokenifier)
        self.cmdwords: list[CommandWord] = []

    def wordify(self, the_string: str) -> list[CommandWord]:
        for line in split_lines(the_string):
            self.handle_line(line)
        return self.cmdwords

    def handle_line(self, line: str) -> None:
        self.tracker.update(line)
        if self.tracker.should_wordify_line(line):
            words = split_words(line)
            self.cmdwords += [  self.factory.create(word, levels=self.tracker.get_levels()) 
                                for word in words]

