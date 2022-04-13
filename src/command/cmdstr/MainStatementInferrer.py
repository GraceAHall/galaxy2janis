

from dataclasses import dataclass

from command.cmdstr.DynamicCommandStatement import DynamicCommandStatement
from xmltool.ToolXMLMetadata import ToolXMLMetadata
from command.cmdstr.utils import global_align


@dataclass
class StatementMetricRecord:
    index: int
    statement: DynamicCommandStatement
    gxrefs: int = 0 # the number of references to galaxy params in the statement
    reqsim: float = 0 # the similarity between the main tool requirement, and the first word of the statement

class MainStatementInferrer:
    def __init__(self, statements: list[DynamicCommandStatement], metadata: ToolXMLMetadata):
        self.statements = statements
        self.main_requirement: str = metadata.get_main_requirement().get_text()
        self.metric_records: list[StatementMetricRecord] = []

    def infer(self) -> int:
        if len(self.statements) <= 1:
            return 0

        self.init_metric_record()
        self.set_gxref_counts()
        self.set_mainreq_similarities()
        return self.choose_best_statement()
        
    def init_metric_record(self) -> None:
        for i, statement in enumerate(self.statements):
            new_record = StatementMetricRecord(i, statement)
            self.metric_records.append(new_record)
        
    def set_gxref_counts(self) -> None:
        for record in self.metric_records:
            record.gxrefs = record.statement.get_galaxy_reference_count()
        
    def set_mainreq_similarities(self) -> None:
        max_possible_score = global_align(self.main_requirement, self.main_requirement)
        for record in self.metric_records:
            if len(record.statement.realised_tokens) == 0:
                record.reqsim = 0
            else:
                raw_similarity = global_align(record.statement.get_first_word(), self.main_requirement)
                record.reqsim = raw_similarity / max_possible_score
    
    def choose_best_statement(self) -> int:
        # TODO statment with most flags? statement with redirect? statement firstword is not in list of known linux commands (except in cases like where the tool is actually 'awk')?

        # same statement at the top of both metrics
        highest_gxrefs = sorted(self.metric_records, key=lambda x: x.gxrefs, reverse=True)[0]
        highest_reqsim = sorted(self.metric_records, key=lambda x: x.reqsim, reverse=True)[0]
        if highest_gxrefs.index == highest_reqsim.index:
            return highest_reqsim.index

        # if 1+ statments firstword is very similar to the tool id (> 80% similar)
        # return the statement in this group with most gxrefs
        candidates = [x for x in self.metric_records if x.reqsim > 0.8]
        if candidates:
            return sorted(candidates, key=lambda x: x.gxrefs, reverse=True)[0].index

        # one statment has at least 3 galaxy references, and this is 2x more than others
        self.metric_records.sort(key=lambda x: x.gxrefs, reverse=True)
        if self.metric_records[0].gxrefs >= 3 and self.metric_records[0].gxrefs >= 2 * self.metric_records[1].gxrefs:
            return self.metric_records[0].index

        # fallback
        return len(self.statements) - 1 # the last statement
      