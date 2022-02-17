

from tool.tool_definition import GalaxyToolDefinition

from command.cmdstr.ConstructTracker import ConstructTracker
from command.cmdstr.utils import split_lines, split_words
from command.cmdstr.CommandWord import CommandWord, CommandWordFactory
from command.tokens.Tokens import TokenType




class CommandWordifier:
    def __init__(self, tool: GalaxyToolDefinition):
        self.tracker = ConstructTracker()
        self.factory = CommandWordFactory(tool)
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
        words = split_words(line)
        # TODO HERE
        for word in words:
            if self.is_kvpair(cmdword):
                out += self.split_kvpair(cmdword)
            else:
                out.append(cmdword)

            self.cmdwords += [  self.factory.create(word, levels=self.tracker.get_levels()) 
                                for word in words]
    
    def post_sentinel(self) -> None:
        sentinel = self.factory.spawn_sentinel()
        self.cmdwords.append(sentinel)




class KeyValExpander:
    def __init__(self, tool: GalaxyToolDefinition):
        self.factory = CommandWordFactory(tool)

    def expand(self, cmdwords: list[CommandWord]) -> list[CommandWord]:
        out: list[CommandWord] = []
        for cmdword in cmdwords:
            if self.is_kvpair(cmdword):
                out += self.split_kvpair(cmdword)
            else:
                out.append(cmdword)
        return out

    def is_kvpair(self, cmdword: CommandWord) -> bool:
        if cmdword.token.type == TokenType.KV_PAIR:
            return True
        return False

    def split_kvpair(self, kv_cmdword: CommandWord) -> list[CommandWord]:
        kv_token = kv_cmdword.token
        
        left_text = str(kv_token.match.group(1))
        delim = str(kv_token.match.group(2))
        right_text = str(kv_token.match.group(3))

        left_cmdword = self.factory.create(left_text, nextword_delim=delim)
        right_cmdword = self.factory.create(right_text, nextword_delim=' ')

        self.transfer_context(kv_cmdword, left_cmdword)
        self.transfer_context(kv_cmdword, right_cmdword)

        return [left_cmdword, right_cmdword]

    def transfer_context(self, source: CommandWord, dest: CommandWord) -> None:
        dest.in_conditional = source.in_conditional
        dest.in_loop = source.in_loop
