
from typing import Any, Tuple
from janis.imports.WorkflowImportHandler import WorkflowImportHandler
import janis.snippets.workflow_snippets as snippets
from tags.TagManager import WorkflowTagManager, ToolTagManager
from workflows.io.WorkflowInput import WorkflowInput
from workflows.io.WorkflowOutput import WorkflowOutput
from workflows.step.values.InputValue import InputValue, InputValueType
from workflows.workflow.WorkflowMetadata import WorkflowMetadata
from workflows.step.WorkflowStep import ToolStep

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

    def format_inputs(self,  wflow_tagman: WorkflowTagManager, inputs: list[WorkflowInput]) -> str:
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

    def format_steps(self, inputs: dict[str, WorkflowInput], steps: dict[str, ToolStep]) -> str:
        out_str = '# STEPS'
        for step_tag, step in steps.items():
            out_str += self.format_step(inputs, step_tag, step)
        out_str += '\n'
        return out_str
    
    def format_step(self, workflow_inputs: dict[str, WorkflowInput], step_tag: str, step: ToolStep) -> str:
        self.step_counter += 1
        out_str: str = '\n'
        tool_tag = step.tool.tag_manager.get(step.tool.get_uuid()) #type: ignore
        out_str += f'# step{self.step_counter}: {tool_tag}\n' # TODO THIS IS A HACK REPLACE WITH TAG_MANAGER
        step_inputs = [(tag, inp) for tag, inp in workflow_inputs.items() if inp.step_id == step.metadata.step_id]
        step_inputs.sort(key=lambda x: x[0])
        for tag, inp in step_inputs:
            out_str += self.format_step_input(tag, inp)
        out_str += self.format_step_body(step_tag, tool_tag, step)
        return out_str

    def format_step_input(self, tag: str, inp: WorkflowInput) -> str:
        self.update_imports(tag, inp)
        return snippets.workflow_input_snippet(
            tag=tag,
            datatype=inp.get_janis_datatype_str(),
            # TODO check whether defaults and values can appear here
            doc=inp.get_docstring()
        )

    def format_step_body(self, step_tag: str, tool_tag: str, step: ToolStep) -> str:
        self.update_imports(tool_tag, step)
        input_values = step.get_tool_tags_values()
        unlinked_values = step.get_unlinked_values()
        formatted_values = self.format_tool_values(input_values)
        return snippets.workflow_step_snippet(
            tag=step_tag, # TODO step tag formatter?
            tool=tool_tag,
            tool_input_values=formatted_values,
            unlinked_values=unlinked_values,
            doc=step.get_docstring()
        )
    
    def format_tool_values(self, tags_inputs: list[Tuple[str, InputValue]]) -> list[Tuple[str, str]]:
        # provides the final list of tool input tags & values. 
        # logic for whether to write inputs if they are default, should wrap with quotes etc
        out: list[Tuple[str, str]] = []
        for tag, input_value in tags_inputs:
            if input_value.is_default_value and not self.include_inputs_with_default_value:
                pass
            else:
                wrapped_value = self.wrap_value(input_value)
                out.append((tag, wrapped_value))
        return out

    def wrap_value(self, inval: InputValue) -> str:
        if self.should_quote(inval):
            return f'"{inval.value}"'
        return str(inval.value)

    def should_quote(self, inval: InputValue) -> bool:
        quoted_types = [InputValueType.STRING, InputValueType.RUNTIME]
        if inval.valtype in quoted_types:
            return True
        return False

    def format_outputs(self, outputs: dict[str, WorkflowOutput]) -> str:
        out_str = '# OUTPUTS\n'
        for tag, out in outputs.items():
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
            case ToolStep():
                self.update_imports_for_tool_step(tag, component)
            case WorkflowOutput():
                self.update_imports_for_workflow_output(component)
            case _:
                pass
    
    def update_imports_for_workflow_input(self, inp: WorkflowInput) -> None:
        self.import_handler.update_datatype_imports(inp.janis_datatypes)
    
    def update_imports_for_tool_step(self, tool_tag: str, step: ToolStep) -> None:
        self.update_imports_for_tool_definition(tool_tag, step)
        self.update_imports_for_tool_inputs(step)
        self.update_imports_for_tool_outputs(step)

    def update_imports_for_tool_definition(self, tool_tag: str, step: ToolStep) -> None:
        tool_path = step.get_definition_path()
        tool_path = tool_path.rsplit('.py')[0]
        tool_path = tool_path.replace('/', '.')
        tool_tag = tool_tag.rstrip('123456789') # same as getting basetag, just dodgy method
        self.import_handler.update_tool_imports(tool_path, tool_tag)

    def update_imports_for_tool_inputs(self, step: ToolStep) -> None:
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

    def update_imports_for_tool_outputs(self, step: ToolStep) -> None:
        pass
        # # step outputs? this is a little weird
        # for output in step.list_outputs():
        #     self.import_handler.update_datatype_imports(output.janis_datatypes)

    def update_imports_for_workflow_output(self, output: WorkflowOutput) -> None:
        self.import_handler.update_datatype_imports(output.janis_datatypes)

    def format_imports(self) -> str:
        return self.import_handler.imports_to_string()
        
