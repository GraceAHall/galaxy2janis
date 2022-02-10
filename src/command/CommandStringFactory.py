







from command.CommandStatement import CommandStatement
from tool.tool_definition import GalaxyToolDefinition
from command.simplify.simplify import TestCommandSimplifier, XMLCommandSimplifier
from command.alias.AliasResolver import AliasResolver
from command.CommandStatement import CommandStatement


class CommandString:
    def __init__(self, statements: list[CommandStatement]):
        pass


class CommandStringFactory:
    def __init__(self, tool: GalaxyToolDefinition):
        self.tool = tool

    def create(self, source: str, raw_string: str) -> CommandString:
        simple_str = self.simplify(source, raw_string)
        resolved_str = self.resolve_aliases(simple_str)
        print()
        #statements = self.create_statements(resolved_str)
        #return CommandString(statements)

    def simplify(self, source: str, the_string: str) -> str:
        strategy_map = {
            'test': TestCommandSimplifier(),
            'xml': XMLCommandSimplifier(),
        }
        strategy = strategy_map[source]
        return strategy.simplify(the_string)

    def resolve_aliases(self, the_string: str) -> str:
        ar = AliasResolver(self.tool)
        return ar.resolve(the_string)

    def create_statements(self, the_string: str) -> list[CommandStatement]:
        pass
        #CommandStatement(cmdstr)


