
from typing import Any, Optional, Tuple
from janis.imports.WorkflowImportHandler import WorkflowImportHandler
import janis.snippets.workflow_snippets as snippets
from workflows.io.WorkflowInput import WorkflowInput
from workflows.io.WorkflowOutput import WorkflowOutput
from workflows.step.values.InputValue import ConnectionInputValue, InputValue, InputValueType, StaticInputValue, WorkflowInputInputValue
from workflows.workflow.Workflow import Workflow
from workflows.step.WorkflowStep import WorkflowStep

"""
Array?
UnionType?
"""

class JanisWorkflowFormatter:
    def __init__(self, workflow: Workflow):
        self.workflow = workflow
        self.step_counter: int = 0
        self.import_handler = WorkflowImportHandler()
        self.include_inputs_with_default_value: bool = False 
        # TODO NOTE ^^^ SHOULD BE CLI RUNTIME SETTING

    def to_janis_definition(self) -> str:
        str_note = self.format_top_note()
        str_path = self.format_path_appends()
        str_metadata = self.format_metadata()
        str_builder = self.format_workflow_builder()
        str_inputs = self.format_inputs()
        str_steps = self.format_steps()
        str_outputs = self.format_outputs()
        str_imports = self.format_imports()
        return str_note + str_path + str_imports + str_metadata + str_builder + str_inputs + str_steps + str_outputs

    def format_top_note(self) -> str:
        metadata = self.workflow.metadata
        return snippets.gxtool2janis_note_snippet(
            workflow_name=metadata.name,
            workflow_version=metadata.version
        )

    def format_path_appends(self) -> str:
        return snippets.path_append_snippet()

    def format_metadata(self) -> str:
        metadata = self.workflow.metadata
        return snippets.metadata_snippet(
            tags=metadata.tags,
            annotation=metadata.annotation,
            version=metadata.version
        )

    def format_workflow_builder(self) -> str:
        metadata = self.workflow.metadata
        comment = '# WORKFLOW DECLARATION'
        section = snippets.workflow_builder_snippet(
            tag=self.workflow.tag_manager.get(self.workflow.get_uuid()),
            version=str(metadata.version),
            doc=metadata.annotation
        )
        return f'{comment}\n{section}\n'

    def format_inputs(self) -> str:
        out_str = '# INPUTS\n'
        for inp in self.workflow.inputs:
            uuid = inp.get_uuid()
            tag = self.workflow.tag_manager.get(uuid)
            if inp.is_galaxy_input_step:
                out_str += self.format_input(tag, inp)
        out_str += '\n'
        return out_str

    def format_input(self, tag: str, inp: WorkflowInput) -> str:
        self.update_imports(tag, inp)
        return snippets.workflow_input_snippet(
            tag=tag,
            datatype=inp.get_janis_datatype_str(),
            # TODO check whether defaults and values can appear here
            doc=self.format_docstring(inp)
        )

    def format_docstring(self, entity: WorkflowStep | WorkflowInput | WorkflowOutput) -> Optional[str]:
        raw_doc = entity.get_docstring()
        if raw_doc:
            return raw_doc.replace('"', "'")
        return None

    def format_steps(self, ) -> str:
        out_str = '# STEPS'
        for step in list(self.workflow.steps.values()):
            out_str += self.format_step(step)
        out_str += '\n'
        return out_str
    
    def format_step(self, step: WorkflowStep) -> str:
        tool_tag = step.tool.tag_manager.get(step.tool.get_uuid()) #type: ignore
        self.step_counter += 1
        out_str: str = '\n'
        out_str += f'# step{self.step_counter}: {tool_tag}\n'
        out_str += self.format_step_workflow_inputs(step)
        out_str += self.format_step_body(step)
        return out_str

    def format_step_workflow_inputs(self, step: WorkflowStep) -> str:
        # for step workflow inputs - get (tag, inp) 
        step_wflow_inputs = [inp for inp in self.workflow.inputs if inp.step_id == step.metadata.step_id]
        step_wflow_inputs = [(self.workflow.tag_manager.get(inp.get_uuid()), inp) for inp in step_wflow_inputs]
        step_wflow_inputs.sort(key=lambda x: x[0])
        out_str: str = ''
        for tag, inp in step_wflow_inputs:
            self.update_imports(tag, inp)
            out_str += snippets.workflow_input_snippet(
                tag=tag,
                datatype=inp.get_janis_datatype_str(),
                doc=self.format_docstring(inp)
            )
        return out_str

    def format_step_body(self, step: WorkflowStep) -> str:
        step_tag = self.workflow.tag_manager.get(step.get_uuid())
        tool_tag = step.tool.tag_manager.get(step.tool.get_uuid()) #type: ignore
        self.update_imports(tool_tag, step)
        linked_values = step.get_tool_tags_values()
        linked_values = self.format_linked_tool_values(linked_values)
        unlinked_values = step.get_unlinked_values()
        unlinked_values = self.format_unlinked_tool_values(unlinked_values)
        return snippets.workflow_step_snippet(
            tag=step_tag,
            tool=tool_tag,
            linked_values=linked_values,
            unlinked_values=unlinked_values, 
            doc=self.format_docstring(step)
        )
    
    def format_linked_tool_values(self, tags_inputs: list[Tuple[str, InputValue]]) -> list[Tuple[str, str]]:
        # provides the final list of tool input tags & values. 
        # logic for whether to write inputs if they are default, should wrap with quotes etc
        out: list[Tuple[str, str]] = []
        for comp_tag, input_value in tags_inputs:
            if input_value.is_default_value and not self.include_inputs_with_default_value:
                pass
            else:
                formatted_value = self.format_value(input_value)
                out.append((comp_tag, formatted_value))
        return out

    def format_unlinked_tool_values(self, unlinked_values: list[InputValue]) -> list[Tuple[str, str]]:
        # (gxvarname, text)
        #UNKNOWN()
        out: list[Tuple[str, str]] = []
        for input_value in unlinked_values:
            tag = f'#UNKNOWN({input_value.gxparam.name})' if input_value.gxparam else '#UNKNOWN'
            formatted_value = self.format_value(input_value)
            out.append((tag, formatted_value))
        return out

    def format_value(self, value: InputValue) -> str:
        match value:
            case ConnectionInputValue():
                # get the step
                step = self.workflow.steps[value.step_id]
                assert(step.tool)
                # get the relevant tool output
                toolout = step.get_output(value.step_output).tool_output
                assert(toolout)
                # get their tags & format
                step_tag = self.workflow.tag_manager.get(step.get_uuid())
                toolout_tag = step.tool.tag_manager.get(toolout.get_uuid())
                text = f'w.{step_tag}.{toolout_tag}'
            case WorkflowInputInputValue():
                input_tag = self.workflow.tag_manager.get(value.input_uuid)
                text = f'w.{input_tag}'
            case StaticInputValue():
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
        if isinstance(inval, StaticInputValue):
            quoted_types = [InputValueType.STRING, InputValueType.RUNTIME]
            if inval.valtype in quoted_types:
                return True
        return False

    def format_outputs(self) -> str:
        out_str = '# OUTPUTS\n'
        for out in self.workflow.outputs:
            uuid = out.get_uuid()
            tag = self.workflow.tag_manager.get(uuid)
            out_str += self.format_output(tag, out)
        out_str += '\n'
        return out_str

    def format_output(self, tag: str, output: WorkflowOutput) -> str:
        self.update_imports(tag, output)
        return snippets.workflow_output_snippet(
            tag=tag,
            datatype=output.get_janis_datatype_str(),
            step_tag=output.step_tag,
            toolout_tag=output.toolout_tag
        )

    def update_imports(self, tag: str, component: Any) -> None:
        match component:
            case WorkflowInput():
                self.update_imports_for_workflow_input(component)
            case WorkflowStep():
                self.update_imports_for_tool_step(tag, component)
            case WorkflowOutput():
                self.update_imports_for_workflow_output(component)
            case _:
                pass
    
    def update_imports_for_workflow_input(self, inp: WorkflowInput) -> None:
        self.import_handler.update_datatype_imports(inp.janis_datatypes)
    
    def update_imports_for_tool_step(self, tool_tag: str, step: WorkflowStep) -> None:
        self.update_imports_for_tool_definition(tool_tag, step)
        self.update_imports_for_tool_inputs(step)
        self.update_imports_for_tool_outputs(step)

    def update_imports_for_tool_definition(self, tool_tag: str, step: WorkflowStep) -> None:
        tool_path = step.get_definition_path()
        tool_path = tool_path.rsplit('.py')[0]
        tool_path = tool_path.replace('/', '.')
        tool_tag = tool_tag.rstrip('123456789') # same as getting basetag, just dodgy method
        self.import_handler.update_tool_imports(tool_path, tool_tag)

    def update_imports_for_tool_inputs(self, step: WorkflowStep) -> None:
        pass
        # # get uuids of tool components with value
        # for inp in step():
        # assert(step.tool)
        # component_uuids = [uuid for uuid, _ in step.list_tool_values()]
        # # get component for each uuid
        # components = [c for c in step.tool.inputs if c.get_uuid() in component_uuids]
        # # get datatypes of that component and update
        # for component in components:
        #     self.import_handler.update_datatype_imports(component.janis_datatypes)

    def update_imports_for_tool_outputs(self, step: WorkflowStep) -> None:
        pass
        # # step outputs? this is a little weird
        # for output in step.list_outputs():
        #     self.import_handler.update_datatype_imports(output.janis_datatypes)

    def update_imports_for_workflow_output(self, output: WorkflowOutput) -> None:
        self.import_handler.update_datatype_imports(output.janis_datatypes)

    def format_imports(self) -> str:
        return self.import_handler.imports_to_string()
        
