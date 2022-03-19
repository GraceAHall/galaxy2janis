



from dataclasses import dataclass
from command.cmdstr.DynamicCommandString import DynamicCommandString
from command.components.CommandComponent import CommandComponent
from containers.Container import Container
from workflows.step.Step import GalaxyWorkflowStep
from xmltool.metadata import Metadata
from janis_definition.JanisFormatter import JanisFormatter




@dataclass
class Tool:
    metadata: Metadata
    cmdstr: DynamicCommandString
    inputs: list[CommandComponent]
    outputs: list[CommandComponent]
    container: Container
    base_command: list[str]

    def to_janis_definition(self) -> str:
        formatter = JanisFormatter()
        str_path = formatter.format_path_appends()
        str_inputs = formatter.format_inputs(self.inputs)
        str_outputs = formatter.format_outputs(self.outputs)
        str_commandtool = formatter.format_commandtool(self.metadata, self.base_command, self.container)
        str_translate = formatter.format_translate_func(self.metadata) 
        str_imports = formatter.format_imports()
        return str_path + str_imports + str_inputs + str_outputs + str_commandtool + str_translate

    def generate_workflow_step(self, galaxy_step: GalaxyWorkflowStep) -> str:
        raise NotImplementedError

    
