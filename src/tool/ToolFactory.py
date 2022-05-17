





from typing import Optional
from command.components.outputs.create import create_output
from tool.Tool import Tool
from xmltool.load import XMLToolDefinition
from command.command import Command
from command.components.CommandComponent import CommandComponent
from containers.fetch import Container
from xmltool.param.OutputParam import OutputParam
from datatypes.DatatypeAnnotator import DatatypeAnnotator



class ToolFactory:
    def __init__(self, xmltool: XMLToolDefinition, command: Command, container: Optional[Container]) -> None:
        self.xmltool = xmltool
        self.command = command
        self.container = container
        self.datatype_annotator = DatatypeAnnotator() 

    def create(self) -> Tool:
        tool = Tool(
            metadata=self.xmltool.metadata,
            raw_command=self.xmltool.raw_command,
            container=self.container,
            base_command=self.get_base_command(),
            gxparam_register=self.xmltool.inputs
        )
        self.supply_inputs(tool)
        self.supply_outputs(tool)
        return tool

    def supply_inputs(self, tool: Tool) -> None:
        self.command.set_cmd_positions()
        inputs = self.command.list_inputs(include_base_cmd=False)
        for inp in inputs:
            self.datatype_annotator.annotate(inp)
            tool.add_input(inp)
    
    def supply_outputs(self, tool: Tool) -> None:
        outputs: list[CommandComponent] = []
        outputs += self.get_redirect_outputs()
        outputs += self.get_input_outputs()
        outputs += self.get_wildcard_outputs()
        outputs += self.get_unknown_outputs(outputs)
        for out in outputs:
            self.datatype_annotator.annotate(out)
            tool.add_output(out)

    def get_redirect_outputs(self) -> list[CommandComponent]:
        # already identified in ExecutionPaths
        return self.command.list_outputs()
    
    def get_input_outputs(self) -> list[CommandComponent]:
        # can be identified by looking at the input components which
        # have attached gxparams which are outputs. 
        # example case: toolname input.fastq -o $outfile
        # the -o option would be picked up as a command component, and the
        # gxparam referred to by $outfile is stored on the command component
        out: list[CommandComponent] = []
        for component in self.command.list_inputs(include_base_cmd=False):
            if component.gxparam and isinstance(component.gxparam, OutputParam):
                out.append(create_output('input', component))
        return out
    
    def get_wildcard_outputs(self) -> list[CommandComponent]:
        # outputs which were not identified in the command
        # usually just because they have a file collection strategy
        # like from_work_dir or a <discover_datatsets> tag as a child
        out: list[CommandComponent] = []
        for gxparam in self.xmltool.list_outputs():
            if hasattr(gxparam, 'wildcard_pattern') and gxparam.wildcard_pattern is not None:
                if not self.command.gxparam_is_attached(gxparam):
                    out.append(create_output('wildcard', gxparam))
        return out
    
    def get_unknown_outputs(self, known_outputs: list[CommandComponent]) -> list[CommandComponent]:
        out: list[CommandComponent] = []
        for gxparam in self.xmltool.list_outputs():
            has_output_component = False
            for output in known_outputs:
                if output.gxparam and output.gxparam.name == gxparam.name:
                    has_output_component = True
                    break
            if not has_output_component:
                out.append(create_output('unknown', gxparam))
        return out

    def verify_outputs(self, outputs: list[CommandComponent]) -> None:
        # just checks we have the same number of outputs identified as CommandComponents
        # as there are in the xmltool's listed output params
        assert(len(self.xmltool.list_outputs()) == len(outputs))

    def get_base_command(self) -> list[str]:
        positionals = self.command.get_base_positionals()
        return [p.get_default_value() for p in positionals]
    