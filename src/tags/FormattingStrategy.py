

from abc import ABC, abstractmethod
from typing import Any
from command.components.CommandComponent import CommandComponent
import tags.formatting_rules as rules

# rules = [
#     formatting_rules.non_alphanumeric,
#     formatting_rules.prohibited_key
#     formatting_rules.capitalisation,
# ]

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
        tag = rules.capitalisation(tag, entity)
        tag = rules.replace_keywords(tag, entity)
        tag = rules.encode(tag)
        return tag

# capitalisation is allowed
class ToolNameStrategy(FormattingStrategy):
    def format(self, starting_text: str, entity: Any) -> str:
        tag = starting_text
        tag = rules.non_alphanumeric(tag, entity)
        tag = rules.numeric(tag, entity)
        tag = rules.numeric_start(tag, entity)
        tag = rules.short_tag(tag, entity)
        #tag = rules.capitalisation(tag, entity)
        tag = rules.replace_keywords(tag, entity)
        tag = rules.encode(tag)
        return tag
        

def get_starting_text(entity_type: str, entity: Any) -> str:
    match entity_type:
        case 'workflow':
            return entity.metadata.name # type: ignore
        case 'workflow_input':
            if entity.is_galaxy_input_step: # type: ignore
                return f'in_{entity.name}' # type: ignore
            else:
                return f'{entity.step_tag}_{entity.name}' # type: ignore
        case 'workflow_step':
            return entity.metadata.wrapper.tool_id # type: ignore
        case 'workflow_output':
            return f'{entity.step_tag}_{entity.toolout_tag}' # type: ignore
        case 'tool':
            return entity.metadata.id # type: ignore
        case 'tool_input':
            return get_tool_input_name(entity)
        case 'tool_output':
            basetag = entity.name
            if basetag.startswith('out'):
                return basetag
            else:
                return f'out_{basetag}'
        case _:
            raise RuntimeError()

def get_tool_input_name(component: CommandComponent) -> str:
    default_name = component.name
    if default_name.isnumeric() and component.gxparam:
        return component.gxparam.name.rsplit('.', 1)[-1]  # adv.reference -> reference (gxvarnames)
    return default_name


STRATEGIES = {
    'workflow': GenericFormattingStrategy(),
    'workflow_input': GenericFormattingStrategy(),
    'workflow_step': GenericFormattingStrategy(),
    'workflow_output': GenericFormattingStrategy(),
    'tool': ToolNameStrategy(),
    'tool_input': GenericFormattingStrategy(),
    'tool_output': GenericFormattingStrategy(),
}

def format_tag(entity_type: str, entity: Any) -> str:
    starting_text = get_starting_text(entity_type, entity)
    strategy = STRATEGIES[entity_type]
    return strategy.format(starting_text, entity)



