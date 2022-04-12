

from abc import ABC, abstractmethod
from typing import Any
import tags.formatters as formatters

basic_formatters = [
    formatters.format_capitalisation,
    formatters.replace_non_alphanumeric,
    formatters.handle_prohibited_key
]

class FormattingStrategy(ABC):

    @abstractmethod
    def format(self, starting_text: str, entity: Any) -> str:
        ...

    def format_basic(self, tag: str) -> str:
        for formatter in basic_formatters:
            tag = formatter(tag)
        return tag


class GenericFormattingStrategy(FormattingStrategy):
    def format(self, starting_text: str, entity: Any) -> str:
        tag = self.format_basic(starting_text)
        tag = formatters.encode(tag)
        return tag

class ToolInputStrategy(FormattingStrategy):
    def format(self, starting_text: str, entity: Any) -> str:
        tag = formatters.handle_short_tag(starting_text, entity)
        tag = self.format_basic(tag)
        tag = formatters.encode(tag)
        return tag

def get_strategy(entity_type: str) -> FormattingStrategy:
    strategy_map = {
        'workflow': GenericFormattingStrategy(),
        'workflow_input': GenericFormattingStrategy(),
        'workflow_step': GenericFormattingStrategy(),
        'workflow_output': GenericFormattingStrategy(),
        'tool': GenericFormattingStrategy(),
        'tool_input': ToolInputStrategy(),
        'tool_output': GenericFormattingStrategy(),
    }
    return strategy_map[entity_type]

def format_tag(starting_text: str, entity_type: str, entity: Any) -> str:
    strategy = get_strategy(entity_type)
    return strategy.format(starting_text, entity)




"""
class WorkflowNameStrategy(FormattingStrategy):
    def format(self, starting_text: str, entity: Any) -> str:
        tag = self.format_basic(starting_text)
        tag = formatters.encode(tag)
        return tag

class WorkflowInputStrategy(FormattingStrategy):
    def format(self, starting_text: str, entity: Any) -> str:
        tag = self.format_basic(starting_text)
        tag = formatters.encode(tag)
        return tag

class WorkflowStepStrategy(FormattingStrategy):
    def format(self, starting_text: str, entity: Any) -> str:
        tag = self.format_basic(starting_text)
        tag = formatters.encode(tag)
        return tag

class WorkflowOutputStrategy(FormattingStrategy):
    def format(self, starting_text: str, entity: Any) -> str:
        tag = self.format_basic(starting_text)
        tag = formatters.encode(tag)
        return tag

class ToolNameStrategy(FormattingStrategy):
    def format(self, starting_text: str, entity: Any) -> str:
        tag = self.format_basic(starting_text)
        tag = formatters.encode(tag)
        return tag

class ToolInputStrategy(FormattingStrategy):
    def format(self, starting_text: str, entity: Any) -> str:
        tag = formatters.handle_short_tag(starting_text, entity)
        tag = self.format_basic(tag)
        tag = formatters.encode(tag)
        return tag

class ToolOutputStrategy(FormattingStrategy):
    def format(self, starting_text: str, entity: Any) -> str:
        tag = self.format_basic(starting_text)
        tag = formatters.encode(tag)
        return tag

"""