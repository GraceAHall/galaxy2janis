


from command.cmdstr.ConstructTracker import ConstructTracker
from command.cmdstr.MainStatementInferrer import MainStatementInferrer
from xmltool.ToolXMLMetadata import ToolXMLMetadata
from command.cmdstr.DynamicCommandStatement import DynamicCommandStatement
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
        
        inferrer = MainStatementInferrer(statements, metadata)
        main_index = inferrer.infer()
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







