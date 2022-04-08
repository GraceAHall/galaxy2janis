
from typing import Any, Tuple
from janis.imports.WorkflowImportHandler import WorkflowImportHandler
import janis.snippets.workflow_snippets as snippets
from tags.TagManager import WorkflowTagManager
from workflows.io.WorkflowInput import WorkflowInput
from workflows.io.WorkflowOutput import WorkflowOutput
from workflows.step.values.InputValue import ConnectionInputValue, InputValue, InputValueType, StaticInputValue, WorkflowInputInputValue
from workflows.workflow.WorkflowMetadata import WorkflowMetadata
from workflows.step.WorkflowStep import WorkflowStep

"""
Array?
UnionType?
"""

class JanisWorkflowFormatter:
    def __init__(self):
        self.step_counter: int = 0
        self.import_handler = WorkflowImportHandler()
        self.include_inputs_with_default_value: bool = False 
        # TODO NOTE ^^^ SHOULD BE CLI RUNTIME SETTING

    def format_top_note(self, metadata: WorkflowMetadata) -> str:
        return snippets.gxtool2janis_note_snippet(
            workflow_name=metadata.name,
            workflow_version=metadata.version
        )

    def format_path_appends(self) -> str:
        return snippets.path_append_snippet()

    def format_metadata(self, metadata: WorkflowMetadata) -> str:
        return snippets.metadata_snippet(
            tags=metadata.tags,
            annotation=metadata.annotation,
            version=metadata.version
        )

    def format_workflow_builder(self, wflow_tagman: WorkflowTagManager, wflow_uuid: str, metadata: WorkflowMetadata) -> str:
        comment = '# WORKFLOW DECLARATION'
        section = snippets.workflow_builder_snippet(
            tag=wflow_tagman.get(wflow_uuid),
            version=str(metadata.version),
            doc=metadata.annotation
        )
        return f'{comment}\n{section}\n'

    def format_inputs(self, wflow_tagman: WorkflowTagManager, inputs: list[WorkflowInput]) -> str:
        out_str = '# INPUTS\n'
        for inp in inputs:
            uuid = inp.get_uuid()
            tag = wflow_tagman.get(uuid)
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
            doc=inp.get_docstring()
        )

    def format_steps(self, wflow_tagman: WorkflowTagManager, wflow_inputs: list[WorkflowInput], steps: list[WorkflowStep]) -> str:
        out_str = '# STEPS'
        for step in steps:
            out_str += self.format_step(wflow_tagman, wflow_inputs, step)
        out_str += '\n'
        return out_str
    
    def format_step(self, wflow_tagman: WorkflowTagManager, wflow_inputs: list[WorkflowInput], step: WorkflowStep) -> str:
        tool_tag = step.tool.tag_manager.get(step.tool.get_uuid()) #type: ignore
        self.step_counter += 1
        out_str: str = '\n'
        out_str += f'# step{self.step_counter}: {tool_tag}\n'
        out_str += self.format_step_workflow_inputs(wflow_tagman, wflow_inputs, step)
        out_str += self.format_step_body(wflow_tagman, wflow_inputs, step)
        return out_str

    def format_step_workflow_inputs(self, wflow_tagman: WorkflowTagManager, wflow_inputs: list[WorkflowInput], step: WorkflowStep) -> str:
        # for step workflow inputs - get (tag, inp) 
        step_wflow_inputs = [inp for inp in wflow_inputs if inp.step_id == step.metadata.step_id]
        step_wflow_inputs = [(wflow_tagman.get(inp.get_uuid()), inp) for inp in step_wflow_inputs]
        step_wflow_inputs.sort(key=lambda x: x[0])
        out_str: str = ''
        for tag, inp in step_wflow_inputs:
            self.update_imports(tag, inp)
            out_str += snippets.workflow_input_snippet(
                tag=tag,
                datatype=inp.get_janis_datatype_str(),
                doc=inp.get_docstring()
            )
        return out_str

    def format_step_body(self, wflow_tagman: WorkflowTagManager, wflow_inputs: list[WorkflowInput], step: WorkflowStep) -> str:
        step_tag = wflow_tagman.get(step.get_uuid())
        tool_tag = step.tool.tag_manager.get(step.tool.get_uuid()) #type: ignore
        self.update_imports(tool_tag, step)
        linked_values = step.get_tool_tags_values()
        linked_values = self.format_linked_tool_values(wflow_tagman, linked_values)
        unlinked_values = step.get_unlinked_values()
        unlinked_values = self.format_unlinked_tool_values(wflow_tagman, unlinked_values)
        return snippets.workflow_step_snippet(
            tag=step_tag,
            tool=tool_tag,
            linked_values=linked_values,
            unlinked_values=unlinked_values, 
            doc=step.get_docstring()
        )
    
    def format_linked_tool_values(self, wflow_tagman: WorkflowTagManager, tags_inputs: list[Tuple[str, InputValue]]) -> list[Tuple[str, str]]:
        # provides the final list of tool input tags & values. 
        # logic for whether to write inputs if they are default, should wrap with quotes etc
        out: list[Tuple[str, str]] = []
        for comp_tag, input_value in tags_inputs:
            if input_value.is_default_value and not self.include_inputs_with_default_value:
                pass
            else:
                formatted_value = self.format_value(wflow_tagman, input_value)
                out.append((comp_tag, formatted_value))
        return out

    def format_unlinked_tool_values(self, wflow_tagman: WorkflowTagManager, unlinked_values: list[InputValue]) -> list[Tuple[str, str]]:
        # (gxvarname, text)
        #UNKNOWN()
        out: list[Tuple[str, str]] = []
        for input_value in unlinked_values:
            tag = f'#UNKNOWN({input_value.gxparam.name})' if input_value.gxparam else '#UNKNOWN'
            formatted_value = self.format_value(wflow_tagman, input_value)
            out.append((tag, formatted_value))
        return out

    def format_value(self, wflow_tagman: WorkflowTagManager, value: InputValue) -> str:
        match value:
            case ConnectionInputValue():
                pass
            case WorkflowInputInputValue():
                input_tag = wflow_tagman.get(value.input_uuid)
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

    def format_outputs(self, wflow_tagman: WorkflowTagManager, outputs: list[WorkflowOutput]) -> str:
        out_str = '# OUTPUTS\n'
        for out in outputs:
            uuid = out.get_uuid()
            tag = wflow_tagman.get(uuid)
            out_str += self.format_output(tag, out)
        out_str += '\n'
        return out_str

    def format_output(self, tag: str, output: WorkflowOutput) -> str:
        self.update_imports(tag, output)
        return snippets.workflow_output_snippet(
            tag=tag,  # TODO tag formatter?
            datatype=output.get_janis_datatype_str(),
            step_tag=output.step_tag,
            step_output=output.step_output
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
        
