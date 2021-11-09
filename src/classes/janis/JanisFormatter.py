


from classes.Logger import Logger
from classes.command.Command import TokenType
from classes.outputs.Outputs import Output
from classes.params.Params import Param

from typing import Union

class JanisFormatter:
    def __init__(self, tool, janis_out_path: str, logger: Logger) -> None:
        self.tool = tool
        self.janis_out_path = janis_out_path
        self.logger = logger

        # janis attributes to create
        self.commandtool: str = ''
        self.inputs: list[str] = []
        self.outputs: list[str] = []
        self.metadata: list[str] = []
        
        self.janis_import_dict: dict[str, set[str]] = {
            'janis_core': {
                'CommandToolBuilder', 
                'ToolInput', 
                'ToolOutput',
                'InputSelector',
                'WildcardSelector',
                'Array',
                'Optional'
            },
            'bioinformatics_types': set(),
            'common_types': set(),
            'unix_types': set(),
        }


    def format(self) -> None:
        self.commandtool = self.gen_commandtool()
        self.inputs = self.gen_inputs()
        self.outputs = self.gen_outputs()
        self.imports = self.gen_imports()
        self.main_call = self.gen_main_call()
        

    def gen_commandtool(self) -> list[str]:
        """
        each str elem in out list is tool output
        """

        base_command = self.infer_base_command()

        toolname = self.tool.id.replace('-', '_')
        container = self.tool.container
        version = self.tool.version

        out_str = f'\n{toolname} = CommandToolBuilder(\n'
        out_str += f'\ttool="{toolname}",\n'
        out_str += f'\tbase_command={base_command},\n'
        out_str += f'\tinputs=inputs,\n'
        out_str += f'\toutputs=outputs,\n'
        out_str += f'\tcontainer="{container}",\n'
        out_str += f'\tversion="{version}",\n'
        # TODO here add requirements (biocontainer for conda pkg or container + version)
        out_str += ')\n'

        return out_str


    def infer_base_command(self) -> str:
        """
        base command is all RAW_STRING tokens before options begin
        can be accessed going through positionals by pos.        
        """
        # get base command positionals
        positionals = self.tool.command.get_positionals()
        positionals = [p for p in positionals if not p.after_options]
        positionals = [p for p in positionals if p.token.type == TokenType.RAW_STRING]

        # remove these positionals 
        for p in positionals:
            self.tool.command.remove_positional(p.pos)

        # format to string
        base_command = [p.token.text for p in positionals]
        base_command = ['"' + cmd + '"' for cmd in base_command]
        base_command = ', '.join(base_command)
        base_command = '[' + base_command + ']'
        return base_command


    def gen_inputs(self) -> list[str]:
        """
        inputs are any positional, flag or option except the following:
            - positional is part of the base_command (will have been removed)
            - positional with TokenType = GX_OUT
            - option with only 1 source token and the TokenType is GX_OUT
            - 
        """
        inputs = []

        



        for param in self.tool.params:
            if param.validated:  # TODO this will rule out complex param syntax at this stage
                param_string = self.format_param_to_string(param) 
                inputs.append(param_string)

        return inputs
        

    def update_datatype_imports(self, entity: Union[Param, Output]) -> None:
        """
        bad naming here. entity because it could be a Param or Output. 
        either way have to update the import list for the datatypes it needs.
        """
        dtype_list = entity.janis_type.split(',')
        for dtype in dtype_list:
            category = self.datatype_categories[dtype]
            self.janis_import_dict[category].add(dtype)


    def format_param_to_string(self, param: Param) -> str:
        """
        ToolInput(
            'fastq1',
            Fastq,
            prefix='--in1',
            doc="First fastq input. If paired end, input2 is used for the other PE fastq"
        )
        """

        self.update_datatype_imports(param)
        jtype = self.format_janis_typestr(param)

        out_str = '\tToolInput(\n'
        out_str += f'\t\t"{param.name}",\n'
        out_str += f'\t\t{jtype},\n'
        out_str += f'\t\tprefix="{param.prefix or ""}",\n'
        out_str += f'\t\tdefault="{param.default_value}",\n'
        out_str += f'\t\tdoc="{param.help_text}"\n'
        out_str += '\t),\n'

        return out_str
        

    def format_janis_typestr(self, param: Param) -> str:
        """
        String
        String(optional=True)
        Array(String(), optional=True)
        """
        janis_type = self.get_janis_type(param) # TODO here
        
        # not array not optional
        if not param.is_optional and not param.is_array:
            out_str = f'{janis_type}'

        # array and not optional
        elif not param.is_optional and param.is_array:
            out_str = f'Array({janis_type})'
        
        # not array and optional
        elif param.is_optional and not param.is_array:
            out_str = f'{janis_type}(optional=True)'
        
        # array and optional
        elif param.is_optional and param.is_array:
            out_str = f'Array({janis_type}(), optional=True)'

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
            self.update_component_imports(output)
            outputs.append(output_string)

        return outputs
        

    def format_output_to_string(self, output: Output) -> str:
        """
        formats outputs into janis tooldef string
        """
        output.janis_type = self.convert_types_to_janis(output)

        out_str = '\tToolOutput(\n'
        out_str += f'\t\t"{output.name}",\n'
        out_str += f'\t\t{output.janis_type},\n'

        # TODO this isnt strictly correct
        out_str += f'\t\tselector={output.selector}("{output.selector_contents}"),\n'
        out_str += f'\t\tdoc="{output.help_text}"\n'
        out_str += '\t),\n'

        return out_str


    def update_component_imports(self, output: Output) -> None:
        """
        need to add the selector type to imports too!
        """
        self.janis_import_dict['janis_core'].add(output.selector)


    def gen_imports(self) -> list[str]:
        out_str = ''
        jid = self.janis_import_dict
        
        # janis core
        if len(jid['janis_core']) > 0:
            modules = ', '.join(jid['janis_core'])
            out_str += f'\nfrom janis_core import {modules}\n'

        # bioinformatics types
        if len(jid['bioinformatics_types']) > 0:
            modules = ', '.join(jid['bioinformatics_types'])
            out_str += f'\nfrom janis_bioinformatics.data_types import {modules}\n'

        # common types
        if len(jid['common_types']) > 0:
            modules = ', '.join(jid['common_types'])
            out_str += f'\nfrom janis_core.types.common_data_types import {modules}\n'

        # unix types
        if len(jid['unix_types']) > 0:
            out_str += '\n'
            for module in jid['unix_types']:
                if module == 'TextFile':  # who even wrote janis
                    out_str += f'from janis_unix.data_types.text import TextFile\n'
                else:
                    out_str += f'from janis_unix.data_types.{module.lower()} import {module}\n'

        return out_str

    
    def gen_main_call(self) -> str:
        """
        generates the __main__ call to translate to wdl on program exec
        """
        toolname = self.tool.tool_id.replace('-', '_')

        out_str = '\n'
        out_str += 'if __name__ == "__main__":\n'
        out_str += f'\t{toolname}().translate(\n'
        out_str += '\t\t"wdl", to_console=True\n'
        out_str += '\t)'
        return out_str
        

    def write(self) -> None:
        """
        writes the text to tool def fil

        """

        with open(self.janis_out_path, 'w') as fp:
            fp.write(self.imports + '\n\n')

            fp.write('inputs = [\n')
            for inp in self.inputs:
                fp.write(inp)
            fp.write(']\n\n')

            fp.write('outputs = [\n')
            for out in self.outputs:
                fp.write(out)
            fp.write(']\n\n')

            fp.write(self.commandtool + '\n')
            fp.write(self.main_call + '\n')



