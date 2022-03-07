

from __future__ import annotations
from enum import Enum, auto
from typing import Any, Optional
from command.tokens.Tokens import Token
from tool.param.OutputParam import DataOutputParam, CollectionOutputParam
from tool.param.Param import Param
from command.components.ValueRecord import PositionalValueRecord

class Stream(Enum):
    STDIN = auto()
    STDOUT = auto()
    STDERR = auto()
    BOTH = auto()

class Tee:
    options: list[Token] = []
    files: list[Token] = []


class StreamMerge:
    def __init__(self, token: Token):
        self.token = token
        self.source: Stream = self.extract_source()
        self.destination: Stream = self.extract_dest()

    def extract_source(self) -> Stream:
        if self.token.text[0] == '2':
            return Stream.STDERR
        return Stream.STDOUT

    def extract_dest(self) -> Stream:
        if self.token.text[-1] == '2':
            return Stream.STDERR
        return Stream.STDOUT


class Redirect:
    def __init__(self, redirect: Token, file: Token):
        self.redirect = redirect
        self.file = file
        self.gxvar: Optional[Param] = file.gxvar
        self.append: bool = True if redirect.text == '>>' else False
        self.stream: Stream = self.extract_stream()
        self.stage: str = 'post_options'
        self.presence_array: list[bool] = []
        self.value_record: PositionalValueRecord = PositionalValueRecord()
        self.value_record.add(0, file.text)

    @property
    def text(self) -> str:
        return self.redirect.text + ' ' + self.file.text

    def extract_stream(self) -> Stream:
        match self.redirect.text[0]:
            case '2':
                return Stream.STDERR
            case _:
                return Stream.STDOUT

    def update(self, incoming: Redirect):
        # transfer galaxy param reference
        if not self.gxvar and incoming.gxvar:
            self.gxvar = incoming.gxvar
        # add values
        self.value_record.record += incoming.value_record.record

    def update_presence_array(self, cmdstr_index: int, fill_false: bool=False):
        pass # TODO

    def get_name(self) -> str:
        # get name from galaxy param if available
        if self.gxvar:
            return self.gxvar.name
        # otherwise, most commonly witnessed option value as name
        pseudo_name = self.value_record.get_most_common_value()
        if pseudo_name:
            return pseudo_name.split('.', 1)[0].split(' ', 1)[0]
        return self.file.text.split('.', 1)[0]

    def get_default_value(self) -> Any:
        return None

    def get_datatype(self) -> list[str]:
        if self.file.gxvar:
            return self.file.gxvar.datatypes
        return ['File']  # TODO what is the fallback type? 
    
    def is_optional(self) -> bool:
        # NOTE - janis does not allow optional outputs
        return False

    def is_array(self) -> bool:
        match self.file.gxvar:
            case CollectionOutputParam() | DataOutputParam():
                return self.file.gxvar.is_array()
            case _:
                pass
        return False

    def get_docstring(self) -> Optional[str]:
        if self.gxvar:
            return self.gxvar.get_docstring()
        return f'examples: {", ".join(self.value_record.get_unique_values()[:3])}'

    # def get_selector(self) -> Selector:
    #     match self.file.gxvar:
    #         case CollectionOutputParam() | DataOutputParam():
    #             if self.file.gxvar.selector:
    #                 return self.file.gxvar.selector
    #         case _:
    #             pass
    #     raise RuntimeError(f'no selector for {self.text}')
        

