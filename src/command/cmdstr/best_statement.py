



from typing import Optional, Tuple
from tool.metadata import Metadata
from command.cmdstr.CommandStatement import CommandStatement
from command.cmdstr.utils import global_align


# TODO this could do with a refactor. is quite ugly.

def get_best_statement(statements: list[CommandStatement], metadata: Metadata) -> CommandStatement:
    if len(statements) == 1:
        return statements[0]
    
    gxref_counts = get_gxref_counts(statements)
    req_similarities = get_requirement_similarities(statements, metadata)
    best = choose_best(gxref_counts, req_similarities)
    
    # return clear best or fallback to last statment
    if best:
        return statements[best]
    return statements[-1]

def get_gxref_counts(statements: list[CommandStatement]) -> list[Tuple[int, int]]:
    out: list[Tuple[int, int]] = []
    for i, statement in enumerate(statements):
        out.append((i, get_stmt_gxref_count(statement)))
    out.sort(key=lambda x: x[1], reverse=True)
    return out

def get_stmt_gxref_count(statement: CommandStatement) -> int:
    count: int = 0
    for cmdword in statement.cmdwords:
        if cmdword.gxvar:
            count += 1
    return count

def get_requirement_similarities(statements: list[CommandStatement], metadata: Metadata) -> list[Tuple[int, float]]:
    main_requirement = metadata.get_main_requirement().get_text()
    raw_similarities = get_raw_similarities(statements, main_requirement)
    adj_similarities = adjust_similarities(raw_similarities, main_requirement)
    return adj_similarities

def get_raw_similarities(statements: list[CommandStatement], mainreq: str) -> dict[int, float]:
    return {i: get_firstword_similarity(stmt, mainreq) for i, stmt in enumerate(statements)}
    
def get_firstword_similarity(statement: CommandStatement, main_requirement: str) -> float:
    if len(statement.cmdwords) == 0:
        return 0
    firstword = statement.cmdwords[0].get_first_token()
    if firstword:
        return global_align(firstword.text, main_requirement)
    return 0

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

    return None