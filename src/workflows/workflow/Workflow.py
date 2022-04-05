

from dataclasses import dataclass, field
from uuid import uuid4

from workflows.workflow.WorkflowMetadata import WorkflowMetadata
from workflows.step.Step import GalaxyWorkflowStep, InputDataStep, ToolStep
from workflows.io.WorkflowOutput import WorkflowOutput
from workflows.io.WorkflowInput import WorkflowInput
from tags.TagManager import WorkflowTagManager
from janis.formatters.JanisWorkflowFormatter import JanisWorkflowFormatter


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
    steps: dict[int, GalaxyWorkflowStep] = field(default_factory=dict)
    inputs: list[WorkflowInput] = field(default_factory=list)
    outputs: list[WorkflowOutput] = field(default_factory=list)
    tag_manager: WorkflowTagManager = WorkflowTagManager()
    steps_inputs_uuid_map: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        self.uuid: str = str(uuid4())
        self.tag_manager.register(
            tag_type='workflow_name',
            uuid=self.get_uuid(),
            entity_info={
                'name': self.metadata.name
            }
        )

    def add_step(self, step: GalaxyWorkflowStep) -> None:
        self.steps[step.metadata.step_id] = step
        self.tag_manager.register(
            tag_type='workflow_step',
            uuid=step.get_uuid(),
            entity_info={'name': step.metadata.step_name}
        )
    
    def add_input(self, w_inp: WorkflowInput) -> None:
        self.inputs.append(w_inp)
        if w_inp.from_input_step:
            name = w_inp.input_name
        else:
            step_tag = self.get_step_tag_by_step_id(w_inp.step_id)
            name = f'{step_tag}_{w_inp.input_name}'
        self.tag_manager.register(
            tag_type='workflow_input',
            uuid=w_inp.get_uuid(),
            entity_info={'name': name}
        )
    
    def add_output(self, w_out: WorkflowOutput) -> None:
        self.outputs.append(w_out)
        name = f'{w_out.step_tag}_{w_out.step_output}'
        self.tag_manager.register(
            tag_type='workflow_output',
            uuid=w_out.get_uuid(),
            entity_info={'name': name}
        )

    def get_step_tag_by_step_id(self, step_id: int) -> str:
        """uuids provide access to identifier tags"""
        step_uuid = self.steps[step_id].get_uuid()
        return self.tag_manager.get('workflow_step', step_uuid)

    def get_uuid(self) -> str:
        return self.metadata.uuid

    def list_input_steps(self) -> list[InputDataStep]:
        return [x for x in self.steps.values() if isinstance(x, InputDataStep)]
    
    def list_tool_steps(self) -> list[ToolStep]:
        return [x for x in self.steps.values() if isinstance(x, ToolStep)]

    def get_tool_steps_tags(self) -> dict[str, ToolStep]:
        """used near end of runtime once tags are stable"""
        out: dict[str, ToolStep] = {}
        for step in self.steps.values():
            if isinstance(step, ToolStep):
                tag = self.tag_manager.get('workflow_step', step.get_uuid())
                out[tag] = step
        return out

    def get_inputs_tags(self) -> dict[str, WorkflowInput]:
        """used near end of runtime once tags are stable"""
        out: dict[str, WorkflowInput] = {}
        for w_input in self.inputs:
            tag = self.tag_manager.get('workflow_input', w_input.get_uuid())
            out[tag] = w_input
        return out
    
    def get_outputs_tags(self) -> dict[str, WorkflowOutput]:
        out: dict[str, WorkflowOutput] = {}
        for w_output in self.outputs:
            tag = self.tag_manager.get('workflow_output', w_output.get_uuid())
            out[tag] = w_output
        return out
    
    def to_janis_definition(self) -> str:
        formatter = JanisWorkflowFormatter()
        str_note = formatter.format_top_note(self.metadata)
        str_path = formatter.format_path_appends()
        str_metadata = formatter.format_metadata(self.metadata)
        str_builder = formatter.format_workflow_builder(self.metadata)
        str_inputs = formatter.format_inputs(self.get_inputs_tags())
        str_steps = formatter.format_steps(self.get_inputs_tags(), self.get_tool_steps_tags())
        str_outputs = formatter.format_outputs(self.get_outputs_tags())
        str_imports = formatter.format_imports()
        return str_note + str_path + str_imports + str_metadata + str_builder + str_inputs + str_steps + str_outputs


    

