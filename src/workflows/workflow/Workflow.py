

from dataclasses import dataclass, field
from typing import Optional
from uuid import uuid4

from workflows.workflow.WorkflowMetadata import WorkflowMetadata
from workflows.step.WorkflowStep import WorkflowStep, InputDataStep, ToolStep
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
    steps: dict[int, WorkflowStep] = field(default_factory=dict)
    inputs: list[WorkflowInput] = field(default_factory=list)
    outputs: list[WorkflowOutput] = field(default_factory=list)
    #steps_inputs_uuid_map: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        self.uuid: str = str(uuid4())
        self.tag_manager: WorkflowTagManager = WorkflowTagManager()
        self.tag_manager.register(
            tag_type='workflow',
            entity=self
        )

    def add_step(self, step: WorkflowStep) -> None:
        self.steps[step.metadata.step_id] = step
        if isinstance(step, InputDataStep):
            tag_type = 'workflow_input_data_step'
        if isinstance(step, ToolStep):
            tag_type = 'workflow_step'
        self.tag_manager.register(
            tag_type=tag_type,
            entity=step
        )
    
    def add_input(self, w_inp: WorkflowInput) -> None:
        self.inputs.append(w_inp)
        self.tag_manager.register(
            tag_type='workflow_input',
            entity=w_inp
        )
    
    def add_output(self, w_out: WorkflowOutput) -> None:
        self.outputs.append(w_out)
        self.tag_manager.register(
            tag_type='workflow_output',
            entity=w_out
        )

    def get_input(self, step_id: Optional[int]=None, input_uuid: Optional[str]=None) -> Optional[WorkflowInput]:
        if step_id is not None:
            return [x for x in self.inputs if x.step_id == step_id][0]
        elif input_uuid is not None:
            return [x for x in self.inputs if x.get_uuid() == input_uuid][0]
        else:
            raise RuntimeError('get_input needs to be supplied either step_id or input_uuid')

    def get_step_tag_by_step_id(self, step_id: int) -> str:
        """uuids provide access to identifier tags"""
        step_uuid = self.steps[step_id].get_uuid()
        return self.tag_manager.get(step_uuid)

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
                tag = self.tag_manager.get(step.get_uuid())
                out[tag] = step
        return out

    def get_inputs_tags(self) -> dict[str, WorkflowInput]:
        """used near end of runtime once tags are stable"""
        out: dict[str, WorkflowInput] = {}
        for w_input in self.inputs:
            tag = self.tag_manager.get(w_input.get_uuid())
            out[tag] = w_input
        return out
    
    def get_outputs_tags(self) -> dict[str, WorkflowOutput]:
        out: dict[str, WorkflowOutput] = {}
        for w_output in self.outputs:
            tag = self.tag_manager.get(w_output.get_uuid())
            out[tag] = w_output
        return out
    
    def to_janis_definition(self) -> str:
        formatter = JanisWorkflowFormatter()
        str_note = formatter.format_top_note(self.metadata)
        str_path = formatter.format_path_appends()
        str_metadata = formatter.format_metadata(self.metadata)
        str_builder = formatter.format_workflow_builder(self.tag_manager, self.get_uuid(), self.metadata)
        str_inputs = formatter.format_inputs(self.tag_manager, self.inputs)
        str_steps = formatter.format_steps(self.tag_manager, self.steps)
        str_outputs = formatter.format_outputs(self.tag_manager, self.outputs)
        # str_inputs = formatter.format_inputs(self.get_inputs_tags())
        # str_steps = formatter.format_steps(self.get_inputs_tags(), self.get_tool_steps_tags())
        # str_outputs = formatter.format_outputs(self.get_outputs_tags())
        str_imports = formatter.format_imports()
        return str_note + str_path + str_imports + str_metadata + str_builder + str_inputs + str_steps + str_outputs


    

