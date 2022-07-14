

from __future__ import annotations
from typing import Optional, Tuple

from ...parser.tokens.Token import Token
from gx.gxtool.param.OutputParam import DataOutputParam, CollectionOutputParam

from .OutputComponent import OutputComponent
from ..linux.streams import Stream
from ...components.ValueRecord import PositionalValueRecord


class RedirectOutput(OutputComponent):
    def __init__(self, tokens: Tuple[Token, Token]):
        super().__init__()
        self.redirect_token = tokens[0]
        self.file_token = tokens[1]
        self.stream: Stream = self.extract_stream()

        self.gxparam = self.file_token.gxparam
        self.value_record: PositionalValueRecord = PositionalValueRecord()
        self.value_record.add(self.file_token.text)

    @property
    def name(self) -> str:
        # get name from galaxy param if available
        if self.gxparam:
            return self.gxparam.name
        # otherwise, most commonly witnessed option value as name
        pseudo_name = self.value_record.get_most_common_value()
        if pseudo_name:
            return pseudo_name.split('.', 1)[0].split(' ', 1)[0]
        return self.file_token.text.split('.', 1)[0]
    
    @property
    def text(self) -> str:
        return self.redirect_token.text + ' ' + self.file_token.text

    @property
    def optional(self) -> bool:
        # NOTE - janis does not allow optional outputs
        return False

    @property
    def array(self) -> bool:
        match self.gxparam:
            case CollectionOutputParam() | DataOutputParam():
                return self.gxparam.array
            case _:
                pass
        return False

    @property
    def docstring(self) -> Optional[str]:
        if self.gxparam:
            return self.gxparam.docstring
        return ''
        #return f'examples: {", ".join(self.value_record.get_unique_values()[:5])}'
    
    def is_append(self) -> bool:
        if self.redirect_token.text == '>>':
            return True
        return False

    def extract_stream(self) -> Stream:
        match self.redirect_token.text[0]:
            case '2':
                return Stream.STDERR
            case _:
                return Stream.STDOUT

    # def get_selector_str(self) -> str:
    #     if self.extract_stream() == Stream.STDOUT:
    #         return 'Stdout()'
    #     else:
    #         return 'Stderr()'

