





from typing import Optional
from command.components.outputs.OutputComponentFactory import OutputComponentFactory
from tool.Tool import Tool
from xmltool.load import XMLToolDefinition
from command.infer import Command
from command.components.CommandComponent import CommandComponent
from containers.fetch import Container
from xmltool.param.OutputParam import OutputParam
from datatypes.DatatypeAnnotator import DatatypeAnnotator


class ToolFactory:
    def __init__(self, xmltool: XMLToolDefinition, command: Command, container: Optional[Container]) -> None:
        self.xmltool = xmltool
        self.command = command
        self.container = container
        self.output_factory = OutputComponentFactory()
        self.datatype_annotator = DatatypeAnnotator() 

    def create(self) -> Tool:
        return Tool(
            metadata=self.xmltool.metadata,
            xmlcmdstr=self.command.xmlcmdstr,
            inputs=self.get_inputs(),
            outputs=self.get_outputs(),
            container=self.container,
            base_command=self.get_base_command()
        )

    def get_inputs(self) -> list[CommandComponent]:
        self.command.set_cmd_positions()
        inputs = self.command.get_inputs()
        for inp in inputs:
            self.datatype_annotator.annotate(inp)
        return inputs
    
    def get_outputs(self) -> list[CommandComponent]:
        outputs: list[CommandComponent] = []
        outputs += self.get_redirect_outputs()
        outputs += self.get_input_outputs()
        outputs += self.get_wildcard_outputs()
        for out in outputs:
            self.datatype_annotator.annotate(out)
        self.verify_outputs(outputs)
        return outputs

    def get_redirect_outputs(self) -> list[CommandComponent]:
        # already identified in ExecutionPaths
        return self.command.get_outputs()
    
    def get_input_outputs(self) -> list[CommandComponent]:
        # can be identified by looking at the input components which
        # have attached gxparams which are outputs. 
        # example case: toolname input.fastq -o $outfile
        # the -o option would be picked up as a command component, and the
        # gxparam referred to by $outfile is stored on the command component
        out: list[CommandComponent] = []
        for component in self.command.get_inputs():
            if component.gxparam and isinstance(component.gxparam, OutputParam):
                out.append(self.output_factory.create_input_output(component))
        return out
    
    def get_wildcard_outputs(self) -> list[CommandComponent]:
        # outputs which were not identified in the command
        # usually just because they have a file collection strategy
        # like from_work_dir or a <discover_datatsets> tag as a child
        out: list[CommandComponent] = []
        for gxparam in self.xmltool.list_outputs():
            if gxparam.wildcard_pattern:
                out.append(self.output_factory.create_wildcard_output(gxparam))
        return out

    def verify_outputs(self, outputs: list[CommandComponent]) -> None:
        # just checks we have the same number of outputs identified as CommandComponents
        # as there are in the xmltool's listed output params
        assert(len(self.xmltool.list_outputs()) == len(outputs))

    def get_base_command(self) -> list[str]:
        positionals = self.command.get_base_positionals()
        return [p.get_default_value() for p in positionals]
    