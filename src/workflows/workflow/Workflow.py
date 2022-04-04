

from dataclasses import dataclass, field


from janis.formatters.JanisWorkflowFormatter import JanisWorkflowFormatter
from tags.TagManager import WorkflowTagManager

from workflows.workflow.WorkflowMetadata import WorkflowMetadata
from workflows.step.Step import GalaxyWorkflowStep, InputDataStep, ToolStep
from workflows.io.WorkflowOutput import WorkflowOutput
from workflows.io.WorkflowInput import WorkflowInput
from uuid import uuid4


@dataclass
class Workflow:
    """
    a Workflow() is the final representation of the galaxy workflow
    being parsed. Includes workflow metadata, inputs, tool steps, and outputs. 
    step_ids are used to lookup key information. 
    each input, step, and output is stored with step_id as key. 
    that way everything can be referenced properly. 
    """
    metadata: WorkflowMetadata
    steps: dict[int, GalaxyWorkflowStep] 
    inputs: list[WorkflowInput] = field(default_factory=list)
    outputs: list[WorkflowOutput] = field(default_factory=list)
    tag_manager: WorkflowTagManager = WorkflowTagManager()

    def __post_init__(self):
        self.uuid: str = str(uuid4())
        self.register_workflow_tag()

    def register_workflow_tag(self) -> None:
        self.tag_manager.register(
            tag_type='workflow_name',
            uuid=self.get_uuid(),
            entity_info={
                'name': self.metadata.name
            }
        )

    def register_step_tags(self) -> None:
        for step in self.steps.values():
            self.tag_manager.register(
                tag_type='workflow_step',
                uuid=step.get_uuid(),
                entity_info={'name': step.metadata.step_name}
            )
    
    def register_tool_tags(self) -> None:
        for step in self.get_tool_steps().values():
            assert(step.tool)
            self.tag_manager.register(
                tag_type='tool_name',
                uuid=step.tool.get_uuid(),
                entity_info={'name': step.tool.metadata.id}
            )
    
    def register_workflow_input_tags(self) -> None:
        for inp in self.inputs:
            self.tag_manager.register(
                tag_type='workflow_input',
                uuid=inp.get_uuid(),
                entity_info={'name': f'{inp.step_tag}_{inp.input_tag}'}
            )
    
    def register_workflow_output_tags(self) -> None:
        for out in self.outputs:
            self.tag_manager.register(
                tag_type='workflow_output',
                uuid=out.get_uuid(),
                entity_info={'name': f'{out.source_tag}_{out.source_output}'}
            )

    def get_uuid(self) -> str:
        return self.metadata.uuid

    def get_input_steps(self) -> dict[int, InputDataStep]:
        return {step_id: step for step_id, step in self.steps.items() if isinstance(step, InputDataStep)}
    
    def get_tool_steps(self) -> dict[str, ToolStep]:
        out: dict[str, ToolStep] = {}
        for step in self.steps.values():
            if isinstance(step, ToolStep):
                tag = self.tag_manager.get('workflow_step', step.get_uuid())
                out[tag] = step
        return out

    def get_inputs(self) -> dict[str, WorkflowInput]:
        out: dict[str, WorkflowInput] = {}
        for w_input in self.inputs:
            tag = self.tag_manager.get('workflow_input', w_input.get_uuid())
            out[tag] = w_input
        return out
    
    def get_outputs(self) -> dict[str, WorkflowOutput]:
        out: dict[str, WorkflowOutput] = {}
        for w_output in self.outputs:
            tag = self.tag_manager.get('workflow_output', w_output.get_uuid())
            out[tag] = w_output
        return out
    
    def get_step_uuid_by_step_id(self, query_id: int) -> str:
        """uuids provide access to identifier tags"""
        input_steps = self.get_input_steps()
        if query_id in self.get_input_steps():
            return input_steps[query_id].get_uuid()
        raise RuntimeError(f'no step with step_id={query_id}')

    def to_janis_definition(self) -> str:
        formatter = JanisWorkflowFormatter()
        str_note = formatter.format_top_note(self.metadata)
        str_path = formatter.format_path_appends()
        str_metadata = formatter.format_metadata(self.metadata)
        str_builder = formatter.format_workflow_builder(self.metadata)
        str_inputs = formatter.format_inputs(self.get_inputs())
        str_steps = formatter.format_steps(self.get_inputs(), self.get_tool_steps())
        str_outputs = formatter.format_outputs(self.get_outputs())
        str_imports = formatter.format_imports()
        return str_note + str_path + str_imports + str_metadata + str_builder + str_inputs + str_steps + str_outputs


    

