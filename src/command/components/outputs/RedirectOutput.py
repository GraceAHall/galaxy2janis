

from __future__ import annotations

from command.components.CommandComponent import BaseCommandComponent
from command.tokens.Tokens import Token
from typing import Any, Optional, Tuple
from xmltool.param.OutputParam import DataOutputParam, CollectionOutputParam
from command.components.ValueRecord import PositionalValueRecord
from command.components.linux import Stream
from datatypes.formatting import format_janis_str

class RedirectOutput(BaseCommandComponent):
    def __init__(self, tokens: Tuple[Token, Token]):
        super().__init__()
        self.redirect_token = tokens[0]
        self.file_token = tokens[1]
        self.stream: Stream = self.extract_stream()

        self.gxparam = self.file_token.gxparam
        self.value_record: PositionalValueRecord = PositionalValueRecord()
        self.value_record.add(self.file_token.text)

    def get_name(self) -> str:
        # get name from galaxy param if available
        if self.gxparam:
            return self.gxparam.name
        # otherwise, most commonly witnessed option value as name
        pseudo_name = self.value_record.get_most_common_value()
        if pseudo_name:
            return pseudo_name.split('.', 1)[0].split(' ', 1)[0]
        return self.file_token.text.split('.', 1)[0]

    def get_default_value(self) -> Any:
        raise NotImplementedError()

    def get_janis_datatype_str(self) -> str:
        """gets the janis datatypes then formats into a string for writing definitions"""
        datatype_str = format_janis_str(
            datatypes=self.janis_datatypes,
            is_optional=self.is_optional(),
            is_array=self.is_array()
        )
        return f'Stdout({datatype_str})'
    
    def is_optional(self) -> bool:
        # NOTE - janis does not allow optional outputs
        return False

    def is_array(self) -> bool:
        match self.gxparam:
            case CollectionOutputParam() | DataOutputParam():
                return self.gxparam.is_array()
            case _:
                pass
        return False

    def is_append(self) -> bool:
        if self.redirect_token.text == '>>':
            return True
        return False
    
    def get_docstring(self) -> Optional[str]:
        if self.gxparam:
            return self.gxparam.get_docstring()
        return ''
        #return f'examples: {", ".join(self.value_record.get_unique_values()[:5])}'

    def update(self, incoming: RedirectOutput):
        # transfer galaxy param reference
        if not self.gxparam and incoming.gxparam:
            self.gxparam = incoming.gxparam
        # add values
        self.value_record.record += incoming.value_record.record

    @property
    def text(self) -> str:
        return self.redirect_token.text + ' ' + self.file_token.text

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

