

from typing import Union, Tuple
import sys 
import io


from classes.Logger import Logger
from classes.command.Command import Flag, Option, Positional, TokenType, Token
from classes.outputs.Outputs import Output
from classes.params.Params import Param


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
        self.datatype_imports: set[str] = set()      
        self.default_imports: dict[str, set[str]] = {
            'janis_core': {
                'CommandToolBuilder', 
                'ToolInput', 
                'ToolOutput',
                'InputSelector',
                'WildcardSelector',
                'Array',
                'Optional',
                'UnionType',
                'Stdout'
            }
        }
        self.extra_prohibited_keys = {
            "identifier",
            "tool",
            "scatter",
            "ignore_missing",
            "output",
            "input",
            "inputs"
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

        toolname = self.tool.id.replace('-', '_').lower()
        version = self.tool.version
        container = self.tool.container
        
        out_str = f'\n{toolname} = CommandToolBuilder(\n'
        out_str += f'\ttool="{toolname}",\n'
        out_str += f'\tbase_command={base_command},\n'
        out_str += f'\tinputs=inputs,\n'
        out_str += f'\toutputs=outputs,\n'

        if self.container_version_mismatch():
            out_str += (f'\t# WARN contaniner version mismatch\n\t# tool requirement version was {self.tool.main_requirement["version"]}\n\t# container version is {container["version"]}\n')

        out_str += f'\tcontainer="{container["url"]}",\n'
        out_str += f'\tversion="{version}",\n'
        out_str += ')\n'

        return out_str


    def container_version_mismatch(self) -> bool:
        target_version = self.tool.main_requirement['version']
        acquired_version = self.tool.container['version']
        if target_version != acquired_version:
            return True
        return False


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

        inputs.append('\t# positionals\n')
        for posit in command.get_positionals():
            new_input = self.format_positional_to_string(posit)
            inputs.append(new_input)

        inputs.append('\t# flags\n')
        for flag in command.get_flags():
            new_input = self.format_flag_to_string(flag)
            inputs.append(new_input)

        inputs.append('\t# options\n')
        for opt in command.get_options():
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
        tag = self.validate_tag(tag)
        docstring = self.validate_docstring(docstring)

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

        return out_str


    def extract_positional_details(self, posit: Positional) -> Tuple[str, str, str, str]:
        token = posit.token
        
        if token.gx_ref != '':
            gx_obj = self.get_gx_obj(token.gx_ref)
            tag = gx_obj.name
            default = gx_obj.get_default()
            if default == '':
                default = None
        else:
            tag = posit.token.text
            default = None

        docstring = self.get_docstring([token])
        datatype = self.format_janis_typestr(posit.datatypes)        

        return tag, datatype, default, docstring


    def validate_tag(self, tag: str) -> str:
        """
        to avoid janis reserved keywords

        """
        if tag in self.extra_prohibited_keys or len(tag) == 1:
            tag += '_janis'

        return tag
    
    
    def validate_docstring(self, docstring: str) -> str:
        """
        to avoid janis reserved keywords

        """
        docstring = docstring.replace('"', '\\"')

        return docstring


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
        tag = self.validate_tag(tag)
        docstring = self.validate_docstring(docstring)

        out_str = '\tToolInput(\n'
        out_str += f'\t\t"{tag}",\n'
        out_str += f'\t\t{datatype},\n'
        out_str += f'\t\tprefix="{prefix}",\n'
        out_str += f'\t\tdoc="{docstring}"\n'
        out_str += '\t),\n'

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
        tag = self.validate_tag(tag)
        docstring = self.validate_docstring(docstring)

        out_str = '\tToolInput(\n'
        out_str += f'\t\t"{tag}",\n'
        out_str += f'\t\t{datatype},\n'

        if opt.delim != ' ':
            out_str += f'\t\tprefix="{prefix + opt.delim}",\n'
            out_str += f'\t\tseparate_value_from_prefix=False,\n'
        else:
            out_str += f'\t\tprefix="{prefix}",\n'

        if default is not None:
            if len(opt.datatypes) == 1 and opt.datatypes[0]['classname'] in ['Float', 'Int']:
                out_str += f'\t\tdefault={default},\n'
            else:
                out_str += f'\t\tdefault="{default}",\n'
        
        out_str += f'\t\tdoc="{docstring}"\n'
        out_str += '\t),\n'

        return out_str


    def extract_option_details(self, opt: Option) -> Tuple[str, str, str, str, str]:
        tag = opt.prefix.lstrip('-')
        datatype = self.format_janis_typestr(opt.datatypes)        
        prefix = opt.prefix

        default = self.get_default(opt.sources)
        if default == '':
            default = None
        docstring = self.get_docstring(opt.sources)

        return tag, datatype, prefix, default, docstring
    

    def get_default(self, tokens: list[Token]) -> str:
        # try from galaxy token first
        for token in tokens:
            if token.gx_ref != '':
                gx_obj = self.get_gx_obj(token.gx_ref)
                return gx_obj.get_default()
        
        # if not
        return tokens[0].text
        

    def format_janis_typestr(self, datatypes: list[str], is_array=False, is_optional=False) -> str:
        """
        String
        String(optional=True)
        Array(String(), optional=True)
        etc
        """

        self.update_datatype_imports(datatypes)

        # just work with the classname now
        datatypes = [d['classname'] for d in datatypes]
        
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

    
    def update_datatype_imports(self, datatypes: list[dict[str, str]]) -> None:
        """
        update the import list for the datatypes it needs.
        """
        for dtype in datatypes:
            import_str = f'from {dtype["import_path"]} import {dtype["classname"]}'
            self.datatype_imports.add(import_str)


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

        for output in self.tool.out_register.get_outputs():
            self.update_component_imports(output)
            output_string = self.format_output_to_string(output) 
            outputs.append(output_string)

        return outputs


    def update_component_imports(self, output: Output) -> None:
        """
        need to add the selector type to imports too!
        """
        self.default_imports['janis_core'].add(output.selector)
        

    def format_output_to_string(self, output: Output) -> str:
        """
        formats outputs into janis tooldef string
        """
        datatype = self.format_janis_typestr(output.datatypes)
        tag = self.validate_tag(output.name)
        docstring = self.validate_docstring(output.help_text)

        out_str = '\tToolOutput(\n'
        out_str += f'\t\t"{tag}",\n'

        if output.is_stdout:
            out_str += f'\t\tStdout({datatype}),\n'
        else:
            out_str += f'\t\t{datatype},\n'
            out_str += f'\t\tselector={output.selector}("{output.selector_contents}"),\n'
        
        out_str += f'\t\tdoc="{docstring}"\n'
        out_str += '\t),\n'

        return out_str


    def gen_imports(self) -> list[str]:
        out_str = ''

        out_str += 'import sys\n'
        out_str += 'import os\n'
        out_str += 'sys.path.append(os.getcwd() + "\\src")\n'
        # default imports from janis core

        if len(self.default_imports['janis_core']) > 0:
            modules = ', '.join(self.default_imports['janis_core'])
            out_str += f'\nfrom janis_core import {modules}\n'

        # all the other datatypes we found
        if len(self.tool.out_register.get_outputs()) > 0:
            self.datatype_imports.add('from janis_core.types.common_data_types import Boolean')
        for import_str in list(self.datatype_imports):
            out_str += f'{import_str}\n'

        return out_str

    
    def gen_main_call(self) -> str:
        """
        generates the __main__ call to translate to wdl on program exec
        """
        toolname = self.tool.id.replace('-', '_')

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

        with open(self.janis_out_path, 'w', encoding="utf-8") as fp:
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




