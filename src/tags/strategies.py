

from typing import Any
from abc import ABC, abstractmethod
from . import rules as rules

class FormattingStrategy(ABC):

    @abstractmethod
    def format(self, starting_text: str, entity: Any) -> str:
        ...

# default
class GenericFormattingStrategy(FormattingStrategy):
    def format(self, starting_text: str, entity: Any) -> str:
        tag = starting_text
        tag = rules.numeric(tag, entity)
        tag = rules.numeric_start(tag, entity)
        tag = rules.non_alphanumeric(tag, entity)
        tag = rules.short_tag(tag, entity)
        tag = rules.replace_keywords(tag, entity)
        #tag = rules.encode(tag)
        tag = rules.camelify(tag)
        return tag

class StepOutputFormattingStrategy(FormattingStrategy):
    def format(self, starting_text: str, entity: Any) -> str:
        tag = starting_text
        tag = rules.numeric(tag, entity)
        tag = rules.numeric_start(tag, entity)
        tag = rules.non_alphanumeric(tag, entity, allow_dot=True)
        tag = rules.short_tag(tag, entity)
        tag = rules.replace_keywords(tag, entity)
        #tag = rules.encode(tag)
        tag = rules.camelify(tag)
        return tag

# capitalisation is allowed
class ToolNameStrategy(FormattingStrategy):
    def format(self, starting_text: str, entity: Any) -> str:
        tag = starting_text
        tag = rules.non_alphanumeric(tag, entity)
        tag = rules.numeric(tag, entity)
        tag = rules.numeric_start(tag, entity)
        tag = rules.short_tag(tag, entity)
        tag = rules.replace_keywords(tag, entity)
        #tag = rules.encode(tag)
        tag = rules.camelify(tag)
        return tag
        

STRATEGIES = {
    'Workflow': GenericFormattingStrategy(),
    'WorkflowInput': GenericFormattingStrategy(),
    'WorkflowStep': GenericFormattingStrategy(),
    'StepOutput': StepOutputFormattingStrategy(),
    'Tool': ToolNameStrategy(),
    'Positional': GenericFormattingStrategy(),
    'Flag': GenericFormattingStrategy(),
    'Option': GenericFormattingStrategy(),
    'RedirectOutput': GenericFormattingStrategy(),
    'WildcardOutput': GenericFormattingStrategy(),
    'InputOutput': GenericFormattingStrategy(),
}


def format_tag(starting_text: str, entity: Any) -> str:
    strategy = STRATEGIES[entity.__class__.__name__]
    return strategy.format(starting_text, entity)



