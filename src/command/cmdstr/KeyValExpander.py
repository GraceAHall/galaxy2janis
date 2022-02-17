
from command.cmdstr.CommandWord import CommandWord
from command.cmdstr.CommandWord import CommandWordFactory
from command.tokens.Tokens import TokenType
from tool.tool_definition import GalaxyToolDefinition


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

