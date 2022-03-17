

from __future__ import annotations
from typing import Optional, Tuple

from tool.tool_definition import GalaxyToolDefinition
from tool.metadata import Metadata

from command.cmdstr.CommandStatement import CommandStatement
from command.simplify.simplify import TestCommandSimplifier, XMLCommandSimplifier
from command.alias.AliasResolver import AliasResolver
from command.regex.scanners import get_statement_delims
from command.cmdstr.utils import global_align
from command.regex.utils import get_quoted_sections

class DynamicCommandString:
    def __init__(self, source: str, statements: list[CommandStatement], metadata: Metadata):
        self.source = source
        self.statements = statements
        self.tool_statement: CommandStatement = get_best_statement(self.statements, metadata)


class DynamicCommandStringFactory:
    def __init__(self, tool: GalaxyToolDefinition):
        self.tool = tool

    def create(self, source: str, raw_string: str) -> DynamicCommandString:
        simple_str = self.simplify_raw_string(source, raw_string)
        statements = self.create_statements(simple_str)
        #statements = self.resolve_statement_aliases(statements)
        statements = self.set_statement_tokens(statements)
        esource = DynamicCommandString(source, statements, self.tool.metadata)
        return esource

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
        ar = AliasResolver(self.tool)
        for cmd_statement in statements:
            ar.extract(cmd_statement)
        for cmd_statement in statements:
            ar.resolve(cmd_statement)
        return statements
        
    def set_statement_tokens(self, statements: list[CommandStatement]) -> list[CommandStatement]:
        for cmd_statement in statements:
            cmd_statement.set_tokens(self.tool)
        return statements

   

def split_to_statements(the_string: str) -> list[CommandStatement]:
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

    return [CommandStatement(stmt, end_delim=delim) for stmt, delim in zip(statements, delims)]

def split_to_statements_old(the_string: str) -> list[CommandStatement]:
    """
    splits a string into individual command line statements.
    these are delimited by &&, ||, | etc
    """
    # TODO HERE
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

def get_best_statement(statements: list[CommandStatement], metadata: Metadata) -> CommandStatement:
    if len(statements) == 1:
        return statements[0]
    
    gxref_counts = get_gxref_counts(statements)
    req_similarities = get_requirement_similarities(statements, metadata)
    best = choose_best(gxref_counts, req_similarities)
    # return clear best or fallback to final statement
    if best:
        return statements[best]
    return statements[-1]

def get_gxref_counts(statements: list[CommandStatement]) -> list[Tuple[int, int]]:
    out: list[Tuple[int, int]] = []
    for i, statement in enumerate(statements):
        out.append((i, statement.get_galaxy_reference_count()))
    out.sort(key=lambda x: x[1], reverse=True)
    return out

def get_requirement_similarities(statements: list[CommandStatement], metadata: Metadata) -> list[Tuple[int, float]]:
    main_requirement = metadata.get_main_requirement().get_text()
    raw_similarities = get_raw_similarities(statements, main_requirement)
    adj_similarities = adjust_similarities(raw_similarities, main_requirement)
    return adj_similarities

def get_raw_similarities(statements: list[CommandStatement], mainreq: str) -> dict[int, float]:
    return {i: get_firstword_similarity(stmt, mainreq) for i, stmt in enumerate(statements)}

def get_firstword_similarity(statement: CommandStatement, main_requirement: str) -> float:
    if len(statement.tokens) == 0:
        return 0
    else:
        return global_align(statement.get_first_word(), main_requirement)

def adjust_similarities(similarities: dict[int, float], main_requirement: str) -> list[Tuple[int, float]]:
    max_possible_score = global_align(main_requirement, main_requirement)
    out = [(key, val / max_possible_score) for key, val in similarities.items()]
    out.sort(key=lambda x: x[1], reverse=True)
    return out

def choose_best(gxref_counts: list[Tuple[int, int]], req_sims: list[Tuple[int, float]]) -> Optional[int]:
    """
    after gathering some metrics to help reveal the tool statment, use these metrics
    to select the statment which looks like it would be the tool execution
    """
    # same statment at the top of both metrics
    if gxref_counts[0][0] == req_sims[0][0]:
        return gxref_counts[0][0]

    # one statment's firstword is very similar to the tool id (> 80% similar)
    if req_sims[0][1] > 0.8:
        return req_sims[0][0]
    
    # one statment has at least 3 galaxy references, and this is 2x more than others
    if gxref_counts[0][1] >= 3 and gxref_counts[0][1] >= 2 * gxref_counts[1][1]:
        return gxref_counts[0][0]

    # TODO statment with most flags? statement with redirect? statement firstword is not in list of known linux commands (except in cases like where the tool is actually 'awk')?
    return None

