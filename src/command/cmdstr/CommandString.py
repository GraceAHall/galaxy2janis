

from typing import Optional

from tool.tool_definition import GalaxyToolDefinition
from tool.metadata import Metadata

from command.cmdstr.CommandStatement import CommandStatement
from command.tokens.Tokenifier import Tokenifier
from command.simplify.simplify import TestCommandSimplifier, XMLCommandSimplifier
from command.alias.AliasResolver import AliasResolver
from command.regex.scanners import get_statement_delims
from command.cmdstr.best_statement import get_best_statement



class CommandString:
    def __init__(self, source: str, statements: list[CommandStatement]):
        self.source = source
        self.statements = statements
        self.tool_statement: Optional[CommandStatement] = None

    def set_tool_statement(self, metadata: Metadata) -> None:
        """guesses which CommandStatement corresponds to tool execution"""
        self.tool_statement = get_best_statement(self.statements, metadata)

   

def split_to_statements(the_string: str) -> list[CommandStatement]:
    """
    splits a string into individual command line statements.
    these are delimited by &&, ||, | etc
    """
    statements: list[str] = []
    delims: list[Optional[str]] = []

    matches = get_statement_delims(the_string)
    matches.sort(key=lambda x: x.start())

    for m in reversed(matches):
        delim: Optional[str] = m[0] # type: ignore
        left_split = the_string[:m.start()]
        right_split = the_string[m.end():]

        # working in reverse, so prepend new statements and delims
        statements = [right_split] + statements
        delims = [delim] + delims

        # update the string to only be to the left of the split
        the_string = left_split

    # add final remaining statment (actually is the first statement)
    # add a None to the end of delims to shift the alignment of stmts and delims
    # last statement doesnt have trailing delim as command ends
    statements = [the_string] + statements
    delims.append(None)

    return [CommandStatement(stmt, end_delim=delim) for stmt, delim in zip(statements, delims)]



class CommandStringFactory:
    def __init__(self, tool: GalaxyToolDefinition):
        self.tool = tool
        self.tokenifier = Tokenifier(self.tool)

    def create(self, source: str, raw_string: str) -> CommandString:
        simple_str = self.simplify_raw_string(source, raw_string)
        statements = self.create_statements(simple_str)
        statements = self.resolve_statement_aliases(statements)
        statements = self.set_statement_cmdwords(statements)
        statements = self.set_statement_attrs(statements)
        cmdstr = CommandString(source, statements)
        cmdstr.set_tool_statement(self.tool.metadata)
        return cmdstr

    def simplify_raw_string(self, source: str, the_string: str) -> str:
        strategy_map = {
            'test': TestCommandSimplifier(),
            'xml': XMLCommandSimplifier(),
        }
        strategy = strategy_map[source]
        return strategy.simplify(the_string)

    def create_statements(self, the_string: str) -> list[CommandStatement]:
        return split_to_statements(the_string)

    def resolve_statement_aliases(self, statements: list[CommandStatement]) -> list[CommandStatement]:
        ar = AliasResolver(self.tool, self.tokenifier)
        for cmd_statement in statements:
            ar.extract(cmd_statement)
        for cmd_statement in statements:
            ar.resolve(cmd_statement)
        return statements
        
    def set_statement_cmdwords(self, statements: list[CommandStatement]) -> list[CommandStatement]:
        for cmd_statement in statements:
            cmd_statement.set_cmdwords(self.tokenifier)
        return statements

    def set_statement_attrs(self, statements: list[CommandStatement]) -> list[CommandStatement]:
        for cmd_statement in statements:
            cmd_statement.set_attrs()
        return statements
