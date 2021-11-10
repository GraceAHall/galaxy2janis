


from classes.Logger import Logger
from classes.command.Command import Flag, Option, Positional, TokenType, Token
from classes.outputs.Outputs import Output
from classes.params.Params import Param

from typing import Union, Tuple

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

        command = self.tool.command
        for posit in command.get_positionals():
            new_input = self.format_positional_to_string(posit)
            inputs.append(new_input)

        for flag in command.flags.values():
            new_input = self.format_flag_to_string(flag)
            inputs.append(new_input)

        for opt in command.options.values():
            new_input = self.format_option_to_string(opt)
            inputs.append(new_input)

        return inputs
        

    def format_positional_to_string(self, positional: Positional) -> str:
        """
        positional example
            - tag
            - input_type 
            - position
            - presents_as (opt) (leave out for now, but may be useful for galaxy wrangling)
            - default 
            - doc
        """
        tag, datatype, default, docstring = self.extract_positional_details(positional)
        out_str = '\tToolInput(\n'
        out_str += f'\t\t"{tag}",\n'
        out_str += f'\t\t{datatype},\n'
        out_str += f'\t\tposition={positional.pos},\n'

        if default is not None:
            if len(positional.datatypes) == 1 and positional.datatypes[0] in ['Float', 'Integer']:
                out_str += f'\t\tdefault={default},\n'
            else:
                out_str += f'\t\tdefault="{default}",\n'
        
        out_str += f'\t\tdoc="{docstring}"\n'
        out_str += '\t),\n'

        print(out_str)
        return out_str


    def extract_positional_details(self, posit: Positional) -> Tuple[str, str, str, str]:
        token = posit.token
        
        if token.gx_ref != '':
            gx_obj = self.get_gx_obj(token.gx_ref)
            tag = gx_obj.name
            default = gx_obj.get_default()
        else:
            tag = posit.token.text
            default = None

        docstring = self.get_docstring([token])
        datatype = self.format_janis_typestr(posit.datatypes)        

        return tag, datatype, default, docstring


    def get_gx_obj(self, query_ref: str):
        obj = self.tool.param_register.get(query_ref)
        if obj is None:
            obj = self.tool.out_register.get(query_ref) 
        return obj


    def format_flag_to_string(self, flag: Flag) -> str:
        """
        flag example
            'cs_string',
            Boolean(optional=True/False),
            prefix="--cs_string",
            doc=""
        """
        tag, datatype, prefix, docstring = self.extract_flag_details(flag)

        out_str = '\tToolInput(\n'
        out_str += f'\t\t"{tag}",\n'
        out_str += f'\t\t{datatype},\n'
        out_str += f'\t\tprefix="{prefix}",\n'
        out_str += f'\t\tdoc="{docstring}"\n'
        out_str += '\t),\n'

        print(out_str)
        return out_str
        

    def extract_flag_details(self, flag: Flag) -> Tuple[str, str, str, str]:
        tag = flag.prefix.lstrip('-')
        datatype = 'Boolean'

        if flag.is_optional():
            datatype += "(optional=True)"

        prefix = flag.prefix
        docstring = self.get_docstring(flag.sources) # get from galaxy param otherwise blank
        
        return tag, datatype, prefix, docstring
        

    def get_docstring(self, tokens: list[Token]) -> str:
        for token in tokens:
            if token.gx_ref != '':
                gx_obj = self.get_gx_obj(token.gx_ref)
                return gx_obj.help_text
        return ''


    def format_option_to_string(self, opt: Option) -> str:
        """
        option example
            'max_len',
            Int(optional=True/False),
            prefix='--max_len1',
            doc="[Optional] Max read length",
        """
        tag, datatype, prefix, default, docstring = self.extract_option_details(opt)
        out_str = '\tToolInput(\n'
        out_str += f'\t\t"{tag}",\n'
        out_str += f'\t\t{datatype},\n'
        out_str += f'\t\tprefix="{prefix}",\n'

        if default is not None:
            if len(opt.datatypes) == 1 and opt.datatypes[0] in ['Float', 'Integer']:
                out_str += f'\t\tdefault={default},\n'
            else:
                out_str += f'\t\tdefault="{default}",\n'
        
        out_str += f'\t\tdoc="{docstring}"\n'
        out_str += '\t),\n'

        print(out_str)
        return out_str


    def extract_option_details(self, opt: Option) -> Tuple[str, str, str, str, str]:
        tag = opt.prefix.lstrip('-')
        datatype = self.format_janis_typestr(opt.datatypes)        
        prefix = opt.prefix

        default = self.get_default(opt.sources)
        docstring = self.get_docstring(opt.sources)

        return tag, datatype, prefix, default, docstring
    

    def get_default(self, tokens: list[Token]) -> str:
        for token in tokens:
            if token.gx_ref != '':
                gx_obj = self.get_gx_obj(token.gx_ref)
                return gx_obj.get_default()
        return None
        

    def format_janis_typestr(self, datatypes: list[str], is_array=False, is_optional=False) -> str:
        """
        String
        String(optional=True)
        Array(String(), optional=True)
        """

        # TODO HERE
        #self.update_datatype_imports(datatypes)
        
        # handle union type
        if len(datatypes) > 1:
            dtype = ', '.join(datatypes)
            dtype = "UnionType(" + dtype + ")"
        else:
            dtype = datatypes[0]

        # not array not optional
        if not is_optional and not is_array:
            out_str = f'{dtype}'

        # array and not optional
        elif not is_optional and is_array:
            out_str = f'Array({dtype})'
        
        # not array and optional
        elif is_optional and not is_array:
            out_str = f'{dtype}(optional=True)'
        
        # array and optional
        elif is_optional and is_array:
            out_str = f'Array({dtype}(), optional=True)'

        return out_str

    
    def update_datatype_imports(self, datatypes: list[str]) -> None:
        """
        bad naming here. entity because it could be a Param or Output. 
        either way have to update the import list for the datatypes it needs.
        """
        for dtype in datatypes:
            category = self.datatype_categories[dtype]
            self.janis_import_dict[category].add(dtype)


    # TODO then here

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





"""
    def format_param_to_string(self, param: Param) -> str:
        # ToolInput(
        #     'fastq1',
        #     Fastq,
        #     prefix='--in1',
        #     doc="First fastq input. If paired end, input2 is used for the other PE fastq"
        # )
        # need to be able to get
        #     - tag
        #     - datatype (always Boolean for flags)
        #     - optionality
        #     - position (positional)
        #     - prefix
        #     - default
        #     - doc


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

"""