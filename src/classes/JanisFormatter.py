


from classes.Logger import Logger
from classes.datastructures.Output import Output
from classes.datastructures.Params import Param
from utils.galaxy_utils import convert_types_to_janis
from classes.parsers.ToolParser import ToolParser


class JanisFormatter:
    def __init__(self, tool: ToolParser, out_def: str) -> None:
        self.tool = tool
        self.out_def = out_def
        self.logger = tool.logger # bad awful yuck
        self.inputs: list[str] = []
        self.outputs: list[str] = []
        self.command: list[str] = []
        self.metadata: list[str] = []
    

    def format(self) -> None:
        self.inputs = self.gen_inputs()
        self.outputs = self.gen_outputs()
        self.command = self.gen_command()
        self.commandtool = self.gen_commandtool()
        

    def gen_inputs(self) -> list[str]:
        """
        each str elem in out list is a tool input        
        """
        inputs = []

        for param in self.tool.params:
            if param.validated:  # TODO this will rule out complex param syntax at this stage
                param_string = self.format_param_to_string(param) 
                inputs.append(param_string)

        return inputs
        

    def format_param_to_string(self, param: Param) -> str:
        """
        ToolInput(
            'fastq1',
            Fastq,
            prefix='--in1',
            doc="First fastq input. If paired end, input2 is used for the other PE fastq"
        )
        """
        # TODO: move this to ParamPostProcessing
        param.janis_type, status = convert_types_to_janis(param)

        if status == 1:  # 0 is ok
            self.logger.log(1, 'datatype conversion for param failed')

        out_str = 'ToolInput(\n'
        out_str += f'"{param.name}",\n'
        out_str += f'{param.janis_type},\n'
        out_str += f'prefix="{param.prefix}",\n'
        out_str += f'default="{param.default_value}",\n'
        out_str += f'doc="{param.help_text}"\n'
        out_str += ')\n'

        return out_str
        

    def gen_outputs(self) -> list[str]:
        """
        each str elem in out list is tool output
        identifier: str,
        datatype: Optional[ParseableType] = None,
        source: Union[Selector, ConnectionSource]=None # or List[Selector, ConnectionSource]
        output_folder: Union[str, Selector, List[Union[str, Selector]]] = None,
        output_name: Union[bool, str, Selector, ConnectionSource] = True, # let janis decide output name
        extension: Optional[str] = None, # file extension if janis names file
        doc: Union[str, OutputDocumentation] = None,

        
        """
        outputs = []

        for output in self.tool.outputs:
            output_string = self.format_output_to_string(output) 
            outputs.append(output_string)

        return outputs
        

    def format_output_to_string(self, output: Output) -> str:
        """
        ToolOutput(
            "html_report_out", 
            File,
            selector=InputSelector("html_report_out")
        )
        """
        output.janis_type, status = convert_types_to_janis(output)

        if status == 1:  # 0 is ok
            self.logger.log(1, 'datatype conversion for param failed')

        out_str = 'ToolOutput(\n'
        out_str += f'"{output.name}",\n'
        out_str += f'{output.janis_type},\n'

        # TODO this isnt strictly correct
        out_str += f'selector="{output.selector}({output.selector_contents})",\n'

        out_str += f'doc="{output.help_text}"\n'
        out_str += ')\n'

        return out_str


    def gen_command(self) -> list[str]:
        """
        each str elem in out list is tool output
        """
        return ''
        

    def gen_commandtool(self) -> list[str]:
        """
        each str elem in out list is tool output
        
        fastp = CommandToolBuilder(
            tool='fastp',
            base_command=["fastp"],
            inputs=fastp_inputs,
            outputs=fastp_outputs,
            container='docker.io/biocontainers/fastp:v0.20.1_cv1',
            version='v0.20.1_cv1'
        )
        """
        toolname = self.tool.tool_name
        
        out_str = f'{toolname} = CommandToolBuilder(\n'
        out_str += f'tool="{toolname}"\n'
        out_str += f'base_command=["{self.command}"]\n'
        out_str += f'inputs=inputs\n'
        out_str += f'outputs=outputs\n'
        # TODO here add requirements (biocontainer for conda pkg or container + version)
        out_str += ')\n'

        return out_str

        

    def write(self) -> None:
        """
        writes the text to tool def fil
        
        # TODO: imports for types: 
        from janis_bioinformatics.data_types import Fastq
        from janis_core.types.common_data_types import Boolean, String, Int, File
        """

        component_imports = """from janis_core import (
            CommandToolBuilder,
            InputSelector,
            ToolInput,
            ToolOutput
        )"""

        with open(self.out_def, 'w') as fp:
            fp.write(component_imports + '\n')

            fp.write('inputs = [\n')
            for inp in self.inputs:
                fp.write(inp + ',\n')
            fp.write(']\n')

            fp.write('outputs = [\n')
            for out in self.outputs:
                fp.write(out + ',\n')
            fp.write(']\n')

            fp.write(self.commandtool + '\n')
