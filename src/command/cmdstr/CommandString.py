


from command.cmdstr.ConstructTracker import ConstructTracker
from xmltool.ToolXMLMetadata import ToolXMLMetadata
from typing import Optional, Tuple
from command.cmdstr.DynamicCommandStatement import DynamicCommandStatement
from command.cmdstr.utils import global_align
from xmltool.ToolXMLMetadata import ToolXMLMetadata
from command.cmdstr.utils import split_lines
from command.tokens.Tokens import Token

class CommandString:
    source: str
    main: DynamicCommandStatement
    preprocessing: list[DynamicCommandStatement]
    postprocessing: list[DynamicCommandStatement]

    def __init__(self, source: str, statements: list[DynamicCommandStatement], metadata: ToolXMLMetadata):
        self.source = source
        self.set_statements(statements, metadata)

    def set_statements(self, statements: list[DynamicCommandStatement], metadata: ToolXMLMetadata):
        self.preprocessing = []
        self.postprocessing = []
        
        main_index = infer_main_tool_statement(statements, metadata)
        for i, statement in enumerate(statements):
            if i < main_index:
                self.preprocessing.append(statement)
            elif i == main_index:
                self.main = statement
            else:
                self.postprocessing.append(statement)

    def get_original_tokens(self) -> list[Token]:
        """gets the original tokenized form of the command string"""
        out: list[Token] = []
        for statement in self.preprocessing:
            out += statement.get_tokens()
        out += self.main.get_tokens()
        for statement in self.postprocessing:
            out += statement.get_tokens()
        return out

    def get_text(self) -> str:
        """pieces back together the overall cmdline string from statements and delims"""
        out: str = ''
        for segment in [self.preprocessing, [self.main], self.postprocessing]:
            for statement in segment:
                if statement.end_delim:
                    out += f'{statement.cmdline} {statement.end_delim}\n'
                else:
                    out += statement.cmdline
        return out

    def get_constant_text(self) -> str:
        out: str = ''
        tracker = ConstructTracker()
        text = self.get_text()
        for line in split_lines(text):
            tracker.update(line)
            if not tracker.is_within_construct():
                out += f'{line}\n'
        return out

    def get_positional(self) -> str:
        raise NotImplementedError()
    
    def get_flag(self) -> str:
        raise NotImplementedError()
    
    def get_option(self) -> str:
        raise NotImplementedError()


def infer_main_tool_statement(statements: list[DynamicCommandStatement], metadata: ToolXMLMetadata) -> int:
    if len(statements) <= 1:
        return 0
    
    gxref_counts = get_gxref_counts(statements)
    req_similarities = get_requirement_similarities(statements, metadata)
    best = choose_best(gxref_counts, req_similarities)
    # return clear best or fallback to final statement
    if best is not None:
        return best
    return len(statements) - 1 # the last statement

def get_gxref_counts(statements: list[DynamicCommandStatement]) -> list[Tuple[int, int]]:
    out: list[Tuple[int, int]] = []
    for i, statement in enumerate(statements):
        out.append((i, statement.get_galaxy_reference_count()))
    out.sort(key=lambda x: x[1], reverse=True)
    return out

def get_requirement_similarities(statements: list[DynamicCommandStatement], metadata: ToolXMLMetadata) -> list[Tuple[int, float]]:
    main_requirement = metadata.get_main_requirement().get_text()
    raw_similarities = get_raw_similarities(statements, main_requirement)
    adj_similarities = adjust_similarities(raw_similarities, main_requirement)
    return adj_similarities

def get_raw_similarities(statements: list[DynamicCommandStatement], mainreq: str) -> dict[int, float]:
    return {i: get_firstword_similarity(stmt, mainreq) for i, stmt in enumerate(statements)}

def get_firstword_similarity(statement: DynamicCommandStatement, main_requirement: str) -> float:
    if len(statement.realised_tokens) == 0:
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




