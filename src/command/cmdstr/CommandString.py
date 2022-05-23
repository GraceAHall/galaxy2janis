


from dataclasses import dataclass

from command.cmdstr.DynamicCommandStatement import DynamicCommandStatement
from command.text.tokens.Tokens import Token


@dataclass
class CommandString:
    main: DynamicCommandStatement
    preprocessing: list[DynamicCommandStatement]
    postprocessing: list[DynamicCommandStatement]

    def get_original_tokens(self) -> list[Token]:
        """gets the original tokenized form of the command string"""
        out: list[Token] = []
        for statement in self.preprocessing:
            out += statement.get_tokens()
        out += self.main.get_tokens()
        for statement in self.postprocessing:
            out += statement.get_tokens()
        return out












    # def get_text(self) -> str:
    #     """pieces back together the overall cmdline string from statements and delims"""
    #     out: str = ''
    #     for segment in [self.preprocessing, [self.main], self.postprocessing]:
    #         for statement in segment:
    #             if statement.end_delim:
    #                 out += f'{statement.cmdline} {statement.end_delim}\n'
    #             else:
    #                 out += statement.cmdline
    #     return out

    # def get_constant_text(self) -> str:
    #     out: str = ''
    #     tracker = ConstructTracker()
    #     text = self.get_text()
    #     for line in split_lines(text):
    #         tracker.update(line)
    #         if not tracker.is_within_construct():
    #             out += f'{line}\n'
    #     return out


