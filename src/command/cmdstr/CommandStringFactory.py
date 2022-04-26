



from typing import Optional

from xmltool.tool_definition import XMLToolDefinition

from command.cmdstr.CommandString import CommandString
from command.cmdstr.DynamicCommandStatement import DynamicCommandStatement
from command.simplify.simplify import TestCommandSimplifier, XMLCommandSimplifier
#from command.alias.AliasResolver import AliasResolver
from command.regex.scanners import get_statement_delims
from command.regex.utils import get_quoted_sections


class CommandStringFactory:
    def __init__(self, xmltool: XMLToolDefinition):
        self.xmltool = xmltool

    def create(self, source: str, raw_string: str) -> CommandString:
        simple_str = self.simplify_raw_string(source, raw_string)
        statements = self.create_statements(simple_str)
        statements = self.set_statement_tokens(statements)
        esource = CommandString(source, statements, self.xmltool.metadata)
        return esource

    def simplify_raw_string(self, source: str, the_string: str) -> str:
        strategy_map = {
            'test': TestCommandSimplifier(),
            'xml': XMLCommandSimplifier(),
        }
        strategy = strategy_map[source]
        return strategy.simplify(the_string)

    def create_statements(self, the_string: str) -> list[DynamicCommandStatement]:
        return split_to_statements(the_string)
        
    def set_statement_tokens(self, statements: list[DynamicCommandStatement]) -> list[DynamicCommandStatement]:
        for cmd_statement in statements:
            cmd_statement.set_realised_tokens(self.xmltool)
        return statements

   

def split_to_statements(the_string: str) -> list[DynamicCommandStatement]:
    """
    splits a string into individual command line statements.
    these are delimited by &&, ||, | etc
    """
    statements: list[str] = []
    delims: list[Optional[str]] = []

    quoted_sections = get_quoted_sections(the_string)
    delim_matches = get_statement_delims(the_string)
    delim_matches.sort(key=lambda x: x.start())

    for m in reversed(delim_matches):
        if quoted_sections[m.start()] == False and quoted_sections[m.end()] == False:
            delim: str = m[0]
            left_split = the_string[:m.start()]
            right_split = the_string[m.end():]

            # working in reverse, so prepend new statements and delims
            statements = [right_split] + statements
            delims = [delim] + delims # type: ignore

            # update the string to only be to the left of the split
            the_string = left_split

    # add final remaining statment (actually is the first statement)
    # add a None to the end of delims to shift the alignment of stmts and delims
    # last statement doesnt have trailing delim as command ends
    statements = [the_string] + statements
    delims.append(None)

    return [DynamicCommandStatement(stmt, end_delim=delim) for stmt, delim in zip(statements, delims)]


