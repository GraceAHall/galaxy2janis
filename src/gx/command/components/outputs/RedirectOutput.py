

from __future__ import annotations
from typing import Optional

from .OutputComponent import OutputComponent
from ..linux.streams import Stream
from ...components.ValueRecord import ValueRecord
from tokens import Token


class RedirectOutput(OutputComponent):
    def __init__(self, redirect_token: Token, file_token: Token):
        super().__init__()
        self.redirect_token = redirect_token
        self.file_token = file_token
        self.stream: Stream = self.extract_stream()

        self.gxparam = self.file_token.gxparam
        self.values: ValueRecord = ValueRecord()
        self.values.add(self.file_token)

    @property
    def name(self) -> str:
        # get name from galaxy param if available
        if self.gxparam:
            return self.gxparam.name
        # otherwise, most commonly witnessed option value as name
        pseudo_name = self.values.most_common_value
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
    def docstring(self) -> Optional[str]:
        if self.gxparam:
            return self.gxparam.docstring
        return ''
        #return f'examples: {", ".join(self.values.unique[:5])}'
    
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

