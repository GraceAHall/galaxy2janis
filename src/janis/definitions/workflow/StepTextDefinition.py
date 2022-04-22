


from abc import ABC
from dataclasses import dataclass
from typing import Optional, Tuple
from janis.imports.Import import Import

from command.components.inputs.Positional import Positional
from command.components.inputs.Flag import Flag
from command.components.inputs.Option import Option

from workflows.step.WorkflowStep import WorkflowStep
from workflows.workflow.Workflow import Workflow
from workflows.step.values.InputValue import ConnectionInputValue, DefaultInputValue, InputValue, InputValueType, StaticInputValue, WorkflowInputInputValue
import janis.definitions.workflow.snippets as snippets


@dataclass
class StepTextDefinition(ABC):
    """
    represents a step definition as it appears to the user.
    in future will include features such as providing documentation,
    line references to xml text to aid user etc. 
    """
    step_count: int
    step: WorkflowStep
    workflow: Workflow
    imports: list[Import]
    # TODO NOTE ^^^ SHOULD BE CLI RUNTIME SETTING

    def get_step_tag(self) -> str:
        return self.workflow.tag_manager.get(self.step.get_uuid())
    
    def get_tool_tag(self) -> str:
        tool = self.step.tool
        assert(tool)
        return tool.tag_manager.get(tool.get_uuid())

    @property
    def title(self) -> str:
        return snippets.step_title_snippet(self.step_count, self.get_tool_tag())
    
    @property
    def foreword(self) -> str:
        return snippets.step_foreward_snippet()
    
    @property
    def pre_task(self) -> str:
        return snippets.pre_task_snippet()

    @property
    def runtime_inputs(self) -> str:
        # following few lines could be workflow method? 
        runtime_inputs = self.step.list_runtime_values()
        workflow_inputs = [ self.workflow.get_input(input_uuid=value.input_uuid) 
                            for value in runtime_inputs]
        workflow_inputs = [x for x in workflow_inputs if x is not None]
        out_str: str = ''
        for wflow_inp in workflow_inputs:
            input_tag = self.workflow.tag_manager.get(wflow_inp.get_uuid())
            dtype_string = wflow_inp.get_janis_datatype_str()
            out_str += snippets.workflow_input_snippet(input_tag, dtype_string)
        return out_str

    @property
    def step_call(self) -> str:
        out: str = ''
        out += 'w.step(\n'
        out += f'\t"{self.get_step_tag()}",\n'
        #out += f'\tscatter="{scatter}",\n' if scatter else ''
        out += f'\t{self.get_tool_tag()}(\n'
        out += self.format_unlinked_inputs()
        out += self.format_linked_nondefault_inputs()
        out += self.format_linked_default_inputs()
        out += '\t)\n'
        out += ')\n'
        return out

    def format_unlinked_inputs(self) -> str:
        out: str = ''
        for input_value in self.step.list_unlinked_values():
            text_value = self.get_input_text_value(input_value)
            out += snippets.step_unlinked_value_snippet(text_value, input_value)
        return out

    def format_linked_nondefault_inputs(self) -> str:
        # linked non-default
        out: str = ''
        linked_values = self.step.list_linked_values()
        non_defaults = [(comp_uuid, value) for comp_uuid, value in linked_values 
                        if not isinstance(value, DefaultInputValue)]
        out += self.format_tool_inputs(non_defaults)
        return out
        
    def format_linked_default_inputs(self) -> str:
        # linked default
        out: str = '\n\t\t# DEFAULTS\n'
        linked_values = self.step.list_linked_values()
        defaults = [(comp_uuid, value) for comp_uuid, value in linked_values 
                    if isinstance(value, DefaultInputValue)]
        out += self.format_tool_inputs(defaults)
        return out

    def format_tool_inputs(self, inputs: list[Tuple[str, InputValue]]) -> str:
        line_len = self.calculate_line_len(inputs)
        out: str = ''
        for comp_uuid, value in inputs:
            tag = self.step.tool.tag_manager.get(comp_uuid) # type: ignore
            text_value = self.get_input_text_value(value)
            out += snippets.step_input_value_snippet(
                line_len=line_len,
                tag_and_value=f'{tag}={text_value},',           # trim=False,
                label=self.get_input_label(value),              # INPUT CONNECTION? RUNTIME VALUE?
                argument=self.get_input_argument(comp_uuid),    # --prefix
                datatype=self.get_input_datatype(comp_uuid)     # FASTQ
            )
        return out

    def get_input_label(self, value: InputValue) -> Optional[str]:
        match value:
            case ConnectionInputValue():
                return 'INPUT CONNECTION'
            case WorkflowInputInputValue():
                if value.is_runtime:
                    return 'RUNTIME VALUE'
            case _:
                pass
        return None
    
    def get_input_argument(self, comp_uuid: str) -> str:
        assert(self.step.tool)
        component = self.step.tool.get_input(comp_uuid)
        if isinstance(component, Positional):
            return 'positional'
        elif isinstance(component, Flag) or isinstance(component, Option):
            return component.prefix
        raise RuntimeError()
    
    def get_input_datatype(self, comp_uuid: str) -> str:
        assert(self.step.tool)
        component = self.step.tool.get_input(comp_uuid)
        return component.janis_datatypes[0].classname

    def calculate_line_len(self, inputs: list[Tuple[str, InputValue]]) -> int:
        max_line_len: int = 0
        for comp_uuid, value in inputs:
            tag = self.step.tool.tag_manager.get(comp_uuid) # type: ignore
            line = f'{tag}={self.get_input_text_value(value)},'
            if len(line) > max_line_len:
                max_line_len = len(line)
        return max_line_len

    def get_input_text_value(self, value: InputValue) -> str:
        match value:
            case ConnectionInputValue():
                step = self.workflow.steps[value.step_id]
                toolout = step.get_output(value.step_output).tool_output
                step_tag = self.workflow.tag_manager.get(step.get_uuid())
                toolout_tag = step.tool.tag_manager.get(toolout.get_uuid()) # type: ignore
                text = f'w.{step_tag}.{toolout_tag}'
            case WorkflowInputInputValue():
                input_tag = self.workflow.tag_manager.get(value.input_uuid)
                text = f'w.{input_tag}'
            case StaticInputValue():
                text = f'{value.value}'
            case DefaultInputValue():
                text = f'{value.value}'
            case _: 
                pass
        wrapped_value = self.wrap(text, value)
        return wrapped_value
    
    def wrap(self, text: str, inval: InputValue) -> str:
        if self.should_quote(inval):
            return f'"{text}"'
        return text

    def should_quote(self, inval: InputValue) -> bool:
        if isinstance(inval, StaticInputValue) or isinstance(inval, DefaultInputValue):
            quoted_types = [InputValueType.STRING, InputValueType.RUNTIME]
            if inval.valtype in quoted_types:
                return True
        return False
    
    @property
    def post_task(self) -> str:
        return snippets.post_task_snippet()
    
    
    
    
    

    
