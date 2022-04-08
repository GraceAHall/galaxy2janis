

from abc import ABC, abstractmethod
from typing import Protocol
import tags.formatters as formatters

basic_formatters = [
    formatters.format_capitalisation,
    formatters.replace_non_alphanumeric,
    formatters.handle_prohibited_key
]

class TaggableEntity(Protocol):
    def get_uuid(self) -> str:
        ...

class FormattingStrategy(ABC):

    @abstractmethod
    def format(self, starting_text: str, entity: TaggableEntity) -> str:
        ...

    def format_basic(self, tag: str) -> str:
        for formatter in basic_formatters:
            tag = formatter(tag)
        return tag


class WorkflowNameStrategy(FormattingStrategy):
    def format(self, starting_text: str, entity: TaggableEntity) -> str:
        tag = self.format_basic(starting_text)
        tag = formatters.encode(tag)
        return tag

class WorkflowInputStrategy(FormattingStrategy):
    def format(self, starting_text: str, entity: TaggableEntity) -> str:
        tag = self.format_basic(starting_text)
        tag = formatters.encode(tag)
        return tag

class WorkflowStepStrategy(FormattingStrategy):
    def format(self, starting_text: str, entity: TaggableEntity) -> str:
        tag = self.format_basic(starting_text)
        tag = formatters.encode(tag)
        return tag

class WorkflowOutputStrategy(FormattingStrategy):
    def format(self, starting_text: str, entity: TaggableEntity) -> str:
        tag = self.format_basic(starting_text)
        tag = formatters.encode(tag)
        return tag

class ToolNameStrategy(FormattingStrategy):
    def format(self, starting_text: str, entity: TaggableEntity) -> str:
        tag = self.format_basic(starting_text)
        tag = formatters.encode(tag)
        return tag

class ToolInputStrategy(FormattingStrategy):
    def format(self, starting_text: str, entity: TaggableEntity) -> str:
        tag = formatters.handle_short_tag(starting_text, entity)
        tag = self.format_basic(tag)
        tag = formatters.encode(tag)
        return tag

class ToolOutputStrategy(FormattingStrategy):
    def format(self, starting_text: str, entity: TaggableEntity) -> str:
        tag = self.format_basic(starting_text)
        tag = formatters.encode(tag)
        return tag


def get_starting_text(entity_type: str, entity: TaggableEntity) -> str:
    match entity_type:
        case 'workflow':
            return entity.metadata.name # type: ignore
        case 'workflow_input':
            if entity.is_galaxy_input_step: # type: ignore
                return f'in_{entity.name}' # type: ignore
            else:
                return f'{entity.step_tag}_{entity.name}' # type: ignore
        case 'workflow_step':
            return entity.metadata.tool_name # type: ignore
        case 'workflow_output':
            return f'out_{entity.step_tag}_{entity.step_output}' # type: ignore
        case 'tool':
            return entity.metadata.id # type: ignore
        case 'tool_input':
            return entity.get_name() # type: ignore
        case 'tool_output':
            return f'out_{entity.get_name()}' # type: ignore
        case _:
            raise RuntimeError()

def get_strategy(entity_type: str) -> FormattingStrategy:
    strategy_map = {
        'workflow': WorkflowNameStrategy(),
        'workflow_input': WorkflowInputStrategy(),
        'workflow_step': WorkflowStepStrategy(),
        'workflow_output': WorkflowOutputStrategy(),
        'tool': ToolNameStrategy(),
        'tool_input': ToolInputStrategy(),
        'tool_output': ToolOutputStrategy(),
    }
    return strategy_map[entity_type]

def format_tag(entity_type: str, entity: TaggableEntity) -> str:
    strategy = get_strategy(entity_type)
    starting_text = get_starting_text(entity_type, entity)
    return strategy.format(starting_text, entity)


