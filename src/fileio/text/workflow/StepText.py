

from dataclasses import dataclass
from functools import cached_property
from typing import Tuple

from entities.workflow.step.step import WorkflowStep
from entities.workflow.step.tool_values import ConnectionInputValue, DefaultInputValue, InputValue, StaticInputValue, WorkflowInputInputValue
from entities.workflow.workflow import Workflow
from fileio.text.TextRender import TextRender

import tags
import formatting
from datatypes.JanisDatatype import JanisDatatype


### HELPER METHODS ### 

def title(step_num: int, step: WorkflowStep) -> str: 
    tool_tag = tags.tool.get(step.tool.uuid).upper()
    title = f'# STEP{step_num}: {tool_tag}'
    border = f'# {"=" * (len(title) - 2)}'
    return f"""\
{border}
{title}
{border}
"""

def note() -> str:
    return"""\"\"\"
FOREWORD ----------
Please see [WEBLINK] for information on RUNTIME VALUES
Please see [WEBLINK] for information on the PRE TASK, TOOL STEP, POST TASK structure
\"\"\"
"""

def pre_task(step: WorkflowStep) -> str:
    # TODO DUMP TEXT
    return '# __PRE_TASK__\n'

def post_task(step: WorkflowStep) -> str:
    # TODO DUMP TEXT
    return '# __POST_TASK__\n'

def input_value(
    line_len: int,
) -> str:
    left = line.tag_and_value
    right = '#'
    if line.special_label:
        right += f' {line.special_label}'
    if line.argument:
        right += f' {line.argument}'
    right += f' [{line.datatype}]'
    if line.default:
        right += f' [GALAXY DEFAULT]'
    justified = f'\t\t{left:<{line_len+2}}{right}\n'
    return justified


### HELPER CLASSES ###

@dataclass
class ToolInputLine:
    tag: str 
    value: str
    special_label: str
    prefix_label: str
    default_label: str
    datatype_label: str

    @cached_property
    # NOTE: I dont like overriding __len__ or any other dunders
    def length(self) -> int:  
        return len(f'{self.tag}={self.value},')


class ToolInputLineFactory:
    # ConnectionInputValue
    # WorkflowInputInputValue
    # StaticInputValue
    # DefaultInputValue

    def create(self, invalue: InputValue) -> ToolInputLine:
        return ToolInputLine(
            tag=self.get_tag(invalue),
            value=self.get_value(invalue),
            special_label=self.get_special_label(invalue),
            prefix_label=self.get_prefix_label(invalue),
            default_label=self.get_default_label(invalue),
            datatype_label=self.get_datatype_label(invalue),
        )

    def get_tag(self, invalue: InputValue) -> str:
        if isinstance(invalue, UnlinkedInputValue):
            return '#UNKNOWN='
        else:
            return tags.tool.get(invalue.foreign_uuid)
    
    def get_value(self, invalue: InputValue) -> str:
        match invalue:
            case ConnectionInputValue():
                step = self.workflow.steps[invalue.step_id]
                toolout = step.outputs.get(invalue.step_output).tool_output
                step_tag = self.workflow.tag_manager.get(step.uuid)
                toolout_tag = step.tool.tag_manager.get(toolout.uuid) # type: ignore
                text = f'w.{step_tag}.{toolout_tag}'
            case WorkflowInputInputValue():
                input_tag = self.workflow.tag_manager.get(invalue.foreign_uuid)
                text = f'w.{input_tag}'
            case StaticInputValue():
                text = f'{invalue.value}'
            case DefaultInputValue():
                text = f'{invalue.value}'
            case _: 
                pass
        wrapped_value = self.wrap(text)
        return wrapped_value
    
    def get_special_label(self, invalue: InputValue) -> str:
        raise NotImplementedError()
    
    def get_prefix_label(self, invalue: InputValue) -> str:
        raise NotImplementedError()
    
    def get_default_label(self, invalue: InputValue) -> str:
        raise NotImplementedError()
    
    def get_datatype_label(self, invalue: InputValue) -> str:
        raise NotImplementedError()

    def wrap(self, text: str) -> str:
        if self.should_quote():
            return f'"{text}"'
        return text
    
    def should_quote(self) -> bool: 
        raise NotImplementedError()


### MAIN CLASS ###

class StepText(TextRender):
    def __init__(
        self, 
        entity: WorkflowStep, 
        workflow: Workflow,
        step_num: int,
        render_note: bool=False,
        render_imports: bool=False,
        render_title: bool=True,
        render_wflow_inputs: bool=True
    ):
        super().__init__()
        self.entity = entity
        self.workflow = workflow
        self.step_num = step_num
        self.render_note = render_note
        self.render_title = render_title
        self.render_imports = render_imports
        self.render_wflow_inputs = render_wflow_inputs
    
    @cached_property
    def lines(self) -> list[ToolInputLine]:

        raise NotImplementedError()
    
    @cached_property
    def line_len(self) -> int:
        return max([line.length for line in self.lines])

    @property
    def imports(self) -> list[Tuple[str, str]]:
        raise NotImplementedError()

    def render(self) -> str:
        out_str: str = ''
        if self.render_note:
            out_str += f'{note()}\n'
        if self.render_imports:
            out_str += f'{formatting.format_imports(self.imports)}\n'
        if self.render_title:
            out_str += f'{title(self.step_num, self.entity)}\n'

        # STEP WORKFLOW INPUTS #      
        # TODO inputs      
        out_str += f'{pre_task(self.entity)}\n'

        # MAIN #
        step = self.entity
        out_str += 'w.step(\n'
        out_str += f'\t"{tags.workflow.get(step.uuid)}",\n'
        #out_str += f'\tscatter="{scatter}",\n' if scatter else ''
        out_str += f'\t{tags.workflow.get(step.tool.uuid)}(\n'
        out_str += self.format_unlinked_inputs()
        out_str += self.format_linked_nondefault_inputs()
        out_str += self.format_linked_default_inputs()
        out_str += '\t)\n'
        out_str += ')\n'
        
        out_str += post_task(self.entity) + '\n'
        return out_str

