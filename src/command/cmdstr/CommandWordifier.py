

from xmltool.tool_definition import XMLToolDefinition

from command.cmdstr.ConstructTracker import ConstructTracker
from command.cmdstr.utils import split_lines, split_to_words
from command.cmdstr.CommandWord import CommandWord, CommandWordFactory
from command.tokens.Tokens import TokenType


class CommandWordifier:
    def __init__(self, xmltool: XMLToolDefinition):
        self.tracker = ConstructTracker()
        self.factory = CommandWordFactory(xmltool)
        self.cmdwords: list[CommandWord] = []

    def wordify(self, the_string: str) -> list[CommandWord]:
        self.refresh_attrs()
        for line in split_lines(the_string):
            self.handle_line(line)
        self.post_sentinel()
        return self.cmdwords

    def refresh_attrs(self) -> None:
        self.tracker = ConstructTracker()
        self.cmdwords = []

    def handle_line(self, line: str) -> None:
        self.tracker.update(line)
        if self.tracker.should_wordify_line(line):
            self.wordify_line(line)
    
    def wordify_line(self, line: str) -> None:
        words = split_to_words(line)
        for text in words:
            cmdword = self.factory.create(text, levels=self.tracker.get_levels())
            if self.is_kvpair(cmdword):
                self.handle_kvpair(cmdword)
            else:
                self.cmdwords.append(cmdword)

    def is_kvpair(self, cmdword: CommandWord) -> bool:
        if cmdword.token.type == TokenType.KV_PAIR:
            return True
        return False

    def handle_kvpair(self, kv_cmdword: CommandWord) -> None:
        left_text = str(kv_cmdword.token.match.group(1))
        delim = str(kv_cmdword.token.match.group(2))
        right_text = str(kv_cmdword.token.match.group(3))

        left_cmdword = self.factory.create(left_text, nextword_delim=delim)
        right_cmdword = self.factory.create(right_text, nextword_delim=' ')
        left_cmdword = self.transfer_context(kv_cmdword, left_cmdword)
        right_cmdword = self.transfer_context(kv_cmdword, right_cmdword)

        self.cmdwords.append(left_cmdword)
        self.cmdwords.append(right_cmdword)

    def transfer_context(self, source: CommandWord, dest: CommandWord) -> CommandWord:
        dest.in_conditional = source.in_conditional
        dest.in_loop = source.in_loop
        return dest

    def post_sentinel(self) -> None:
        sentinel = self.factory.spawn_end_sentinel()
        self.cmdwords.append(sentinel)


