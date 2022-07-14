

from dataclasses import dataclass
from functools import cached_property
from typing import Optional, Tuple

from entities.workflow import Workflow
from entities.workflow import WorkflowStep
from entities.workflow import InputValue, ConnectionInputValue, StaticInputValue, WorkflowInputInputValue
from gx.command.components import Positional

from .WorkflowInputText import WorkflowInputText
from ..TextRender import TextRender
from .. import formatting
from .. import ordering

import tags
import datatypes


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

def pre_task(step: WorkflowStep) -> Optional[str]:
    if step.preprocessing:
        out_str: str = ''
        out_str += '# UNTRANSLATED PRE-PROCESSING LOGIC:\n'
        out_str += step.preprocessing
        return out_str
    else:
        return None

def post_task(step: WorkflowStep) -> Optional[str]:
    if step.postprocessing:
        out_str: str = ''
        out_str += '# UNTRANSLATED POST-PROCESSING LOGIC:\n'
        out_str += step.postprocessing
        return out_str
    else:
        return None

### HELPER CLASSES ###

@dataclass
class ToolInputLine:
    tag_and_value: str 
    special_label: str
    prefix_label: str
    default_label: str
    datatype_label: str

    @cached_property
    # NOTE: I dont like overriding __len__ or any other dunders
    def length(self) -> int:  
        return len(f'{self.tag_and_value},')

    def render(self, info_indent: int) -> str:
        left = f'{self.tag_and_value},'
        right = f'#'
        if self.prefix_label != '':
            right += f' {self.prefix_label}'
        if self.special_label != '':
            right += f' ({self.special_label})'
        if self.default_label != '':
            right += f' ({self.default_label})'
        if self.datatype_label != '':
            right += f' [{self.datatype_label}]'
        justified = f'\t\t{left:<{info_indent+2}}{right}'
        return justified


class ToolInputLineFactory:

    def create(self, invalue: InputValue) -> ToolInputLine:
        return ToolInputLine(
            tag_and_value=invalue.tag_and_value,
            special_label=self.get_special_label(invalue),
            prefix_label=self.get_prefix_label(invalue),
            default_label=self.get_default_label(invalue),
            datatype_label=self.get_datatype_label(invalue),
        )

    def get_special_label(self, invalue: InputValue) -> str:
        if isinstance(invalue, WorkflowInputInputValue):
            if invalue.is_runtime:
                return 'RUNTIME VALUE'
            else:
                return 'WORKFLOW INPUT'
        if isinstance(invalue, ConnectionInputValue):
            return 'CONNECTION'
        return ''
    
    def get_prefix_label(self, invalue: InputValue) -> str:
        if invalue.component:
            if hasattr(invalue.component, 'prefix'):
                return invalue.component.prefix  # type: ignore
            elif isinstance(invalue, Positional):
                return f'position {invalue.cmd_pos}'
        return ''
    
    def get_default_label(self, invalue: InputValue) -> str:
        if isinstance(invalue, StaticInputValue):
            if invalue.default:
                return 'GALAXY DEFAULT'
        return ''
    
    def get_datatype_label(self, invalue: InputValue) -> str:
        # TODO here - can maybe follow step connections? 
        if invalue.component:
            jtypes = datatypes.get(invalue.component)
            return jtypes[0].classname
        return ''


### MAIN CLASS ###

class StepText(TextRender):
    def __init__(
        self, 
        step_num: int,
        entity: WorkflowStep, 
        janis: Workflow,
        render_note: bool=False,
        render_imports: bool=False,
        render_title: bool=True,
        render_wflow_inputs: bool=True
    ):
        super().__init__()
        self.step_num = step_num
        self.entity = entity
        self.janis = janis
        self.render_note = render_note
        self.render_title = render_title
        self.render_imports = render_imports
        self.render_wflow_inputs = render_wflow_inputs
    
    @cached_property
    def lines(self) -> list[ToolInputLine]:
        invalues = self.entity.inputs.all
        invalues = ordering.order_step_inputs(invalues)
        factory = ToolInputLineFactory()
        return [factory.create(x) for x in invalues]
    
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

        out_str += f'{self.format_runtime_inputs()}\n'

        preprocessing = pre_task(self.entity)
        if preprocessing:
            out_str += f'"""\n{preprocessing}\n"""\n'

        out_str += f'{self.format_step()}\n'

        postprocessing = post_task(self.entity)
        if postprocessing:
            out_str += f'"""\n{postprocessing}\n"""\n'

        return out_str

    def format_runtime_inputs(self) -> str:
        inputs = self.entity.inputs.all
        inputs = [x for x in inputs if isinstance(x, WorkflowInputInputValue)]
        inputs = [x for x in inputs if x.is_runtime]
        winps = [self.janis.get_input(x.input_uuid) for x in inputs]
        out_str = ''
        for winp in winps:
            out_str += f'{WorkflowInputText(winp).render()}\n'
        return out_str

    def format_step(self) -> str:
        out_str: str = ''
        step_tag = tags.workflow.get(self.entity.uuid)
        tool_tag = tags.tool.get(self.entity.tool.uuid)
        out_str += 'w.step(\n'
        out_str += f'\t"{step_tag}",\n'
        out_str += f'\t{tool_tag}(\n'
        #out_str += f'\tscatter="{scatter}",\n' if scatter else ''
        # input values
        for line in self.lines:
            out_str += f'{line.render(self.line_len)}\n'
        out_str += '\t)\n'
        out_str += ')\n\n'
        return out_str

        

