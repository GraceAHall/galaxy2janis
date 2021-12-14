

from typing import Tuple, Union
from datetime import date

from sqlalchemy.orm import base
from classes.janis.DatatypeExtractor import DatatypeExtractor

from classes.logging.Logger import Logger
from classes.command.Command import Flag, Option, Positional, TokenType, Token
from galaxy.tool_util.parser.output_objects import ToolOutput

CommandComponent = Union[Positional, Flag, Option]


class JanisFormatter:
    def __init__(self, tool, janis_out_path: str, logger: Logger) -> None:
        self.tool = tool
        self.janis_out_path = janis_out_path
        self.logger = logger
        self.dtype_extractor = DatatypeExtractor(logger)

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
        # TODO HERE
        self.outputs = self.gen_outputs()
        self.imports = self.gen_imports()
        self.main_call = self.gen_main_call()
        

    def gen_commandtool(self) -> list[str]:
        """
        each str elem in out list is tool output
        - contributors
        - dateCreated
        - dateUpdated
        """

        base_command = self.infer_base_command()
        toolname = self.tool.id.replace('-', '_').lower()
        version = self.tool.version
        container = self.tool.container
        citation = "NOT NOW ILL DO IT LATER"
        # citaiton = self.tool.get_main_citation()
        
        out_str = f'\n{toolname} = CommandToolBuilder(\n'
        out_str += f'\ttool="{toolname}",\n'
        out_str += f'\tbase_command={base_command},\n'
        out_str += f'\tinputs=inputs,\n'
        out_str += f'\toutputs=outputs,\n'

        if self.container_version_mismatch():
            out_str += (f'\t# WARN contaniner version mismatch\n\t# tool requirement version was {self.tool.main_requirement["version"]}\n\t# container version is {container["version"]}\n')

        out_str += f'\tcontainer="{container["url"]}",\n'
        out_str += f'\tversion="{version}",\n'
        out_str += f'\ttool_provider="{citation}",\n'
        out_str += f'\tcontributors="janis",\n'
        out_str += f'\tdateCreated="{date.today()}",\n'
        out_str += f'\tdateUpdated="{date.today()}",\n'
        out_str += f'\tdocumentation="""{self.tool.help}""",\n'
        out_str += ')\n'

        return out_str


    def infer_base_command(self) -> str:
        """
        base command is all positionals before options begin, where all sources are RAW_STRING types and only 1 value was witnessed.    
        """
        # get positionals before opts
        positionals = self.tool.command.get_positionals()
        positionals = [p for p in positionals if not p.after_options]

        # get positionals which are part of base command
        base_positionals = []
        for p in positionals:
            p_types = p.get_token_types()
            if TokenType.RAW_STRING in p_types and len(p_types) == 1 and p.has_unique_value():
                base_positionals.append(p)

        # remove these Positional CommandComponents as they are now considered 
        # base command, not positionals
        for p in base_positionals:
            self.tool.command.remove_positional(p.pos)

        # format to string
        base_command = [p.get_values(tolist=True)[0] for p in base_positionals]
        base_command = ['"' + cmd + '"' for cmd in base_command]
        base_command = ', '.join(base_command)
        base_command = '[' + base_command + ']'
        return base_command


    def container_version_mismatch(self) -> bool:
        target_version = self.tool.main_requirement['version']
        acquired_version = self.tool.container['version']
        if target_version != acquired_version:
            return True
        return False


    def gen_inputs(self) -> list[str]:
        """
        inputs are any positional, flag or option except the following:
            - positional is part of the base_command (will have been removed)
            - positional with TokenType = GX_OUT
            - option with only 1 source token and the TokenType is GX_OUT
        """
        inputs = []

        command = self.tool.command

        inputs.append('\n\t# positionals\n')
        for posit in command.get_positionals():
            new_input = self.format_positional_to_string(posit)
            inputs.append(new_input)

        inputs.append('\n\t# flags\n')
        for flag in command.get_flags():
            new_input = self.format_flag_to_string(flag)
            inputs.append(new_input)

        inputs.append('\n\t# options\n')
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
        tag, datatypes, default, docstring = self.extract_positional_details(positional)
        tag = self.validate_tag(tag)
        docstring = self.validate_docstring(docstring)
        typestring = self.format_typestring(positional, datatypes)

        out_str = '\tToolInput(\n'
        out_str += f'\t\t"{tag}",\n'
        out_str += f'\t\t{typestring},\n'
        out_str += f'\t\tposition={positional.pos},\n'

        # pure jank
        if default is not None:
            if len(datatypes) == 1 and datatypes[0]['classname'] in ['Float', 'Integer']:
                out_str += f'\t\tdefault={default},\n'
            else:
                out_str += f'\t\tdefault="{default}",\n'
        
        out_str += f'\t\tdoc="{docstring}"\n'
        out_str += '\t),\n'

        return out_str


    def extract_positional_details(self, posit: Positional) -> Tuple[str, str, str, str]:       
        if posit.galaxy_object is not None:
            tag = posit.name
        else:
            tag = '_'.join(posit.get_values(as_list=True))
        
        default = posit.get_default()    
        docstring = self.get_docstring(posit)
        datatypes = self.dtype_extractor.extract(posit)        

        return tag, datatypes, default, docstring


    def validate_tag(self, tag: str) -> str:
        """
        to satisfy janis tag requirements
        to avoid janis reserved keywords
        """
        tag = tag.replace('-', '_')
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
        varname, obj = self.tool.param_register.get(query_ref)
        if obj is None:
            varname, obj = self.tool.out_register.get(query_ref) 
        return varname, obj


    def format_flag_to_string(self, flag: Flag) -> str:
        """
        flag example
            'cs_string',
            Boolean(optional=True/False),
            prefix="--cs_string",
            doc=""
        """
        tag, typestring, prefix, position, docstring = self.extract_flag_details(flag)
        tag = self.validate_tag(tag)
        docstring = self.validate_docstring(docstring)

        out_str = '\tToolInput(\n'
        out_str += f'\t\t"{tag}",\n'
        out_str += f'\t\t{typestring},\n'
        out_str += f'\t\tprefix="{prefix}",\n'
        out_str += f'\t\tposition={position},\n'
        out_str += f'\t\tdoc="{docstring}"\n'
        out_str += '\t),\n'

        return out_str
        

    def extract_flag_details(self, flag: Flag) -> Tuple[str, str, str, str]:
        tag = flag.prefix.lstrip('-')
        typestring = 'Boolean'

        if flag.is_optional():
            typestring += "(optional=True)"

        prefix = flag.prefix
        position = flag.pos
        docstring = self.get_docstring(flag) 
        
        return tag, typestring, prefix, position, docstring
        

    def get_docstring(self, component: CommandComponent) -> str:
        if component.galaxy_object is not None:
            docstring = component.galaxy_object.label + ' ' + component.galaxy_object.help
        elif type(component) in [Positional, Option]:
            values = component.get_values(as_list=True)
            docstring = f'possible values: {", ".join(values[:5])}'
        else:
            docstring = ''

        return docstring


    def format_option_to_string(self, opt: Option) -> str:
        """
        option example
            'max_len',
            Int(optional=True/False),
            prefix='--max_len1',
            doc="[Optional] Max read length",
        """
        tag, datatypes, prefix, default, position, docstring = self.extract_option_details(opt)
        tag = self.validate_tag(tag)
        docstring = self.validate_docstring(docstring)
        typestring = self.format_typestring(opt, datatypes)

        out_str = '\tToolInput(\n'
        out_str += f'\t\t"{tag}",\n'
        out_str += f'\t\t{typestring},\n'

        if opt.delim != ' ':
            out_str += f'\t\tprefix="{prefix + opt.delim}",\n'
            out_str += f'\t\tseparate_value_from_prefix=False,\n'
        else:
            out_str += f'\t\tprefix="{prefix}",\n'

        out_str += f'\t\tposition={position},\n'
        
        if default is not None:
            if len(datatypes) == 1 and datatypes[0]['classname'] in ['Float', 'Integer']:
                out_str += f'\t\tdefault={default},\n'
            else:
                out_str += f'\t\tdefault="{default}",\n'
        
        out_str += f'\t\tdoc="{docstring}"\n'
        out_str += '\t),\n'

        return out_str


    def extract_option_details(self, opt: Option) -> Tuple[str, list[dict], str, str, str]:
        tag = opt.prefix.lstrip('-')
        datatypes = self.dtype_extractor.extract(opt)  
        prefix = opt.prefix
        default = opt.get_default()
        position = opt.pos          
        docstring = self.get_docstring(opt)
        return tag, datatypes, prefix, default, position, docstring
            

    def format_typestring(self, component: CommandComponent, datatypes: list[dict]) -> str:
        """
        turns a component and datatype dict into a formatted string for janis definition.
        the component is used to help detect array / optionality. 
            String
            String(optional=True)
            Array(String(), optional=True)
            etc
        """

        self.update_datatype_imports(datatypes)
        
        # just work with the classname for now
        datatypes = [d['classname'] for d in datatypes]
        
        # handle union type
        if len(datatypes) > 1:
            dtype = ', '.join(datatypes)
            dtype = "UnionType(" + dtype + ")"
        else:
            dtype = datatypes[0]
        
        # not array not optional
        if not component.is_optional() and not component.is_array():
            out_str = f'{dtype}'

        # array and not optional
        elif not component.is_optional() and component.is_array():
            out_str = f'Array({dtype})'
        
        # not array and optional
        elif component.is_optional() and not component.is_array():
            out_str = f'{dtype}(optional=True)'
        
        # array and optional
        elif component.is_optional() and component.is_array():
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
        """
        outputs = []

        for output in self.tool.out_register.get_outputs():
            self.update_component_imports(output)
            output_string = self.format_output_to_string(output) 
            outputs.append(output_string)

        return outputs


    def update_component_imports(self, output: ToolOutput) -> None:
        """
        need to add the selector type to imports too!
        """
        self.default_imports['janis_core'].add(output.selector)
        

    def format_output_to_string(self, output: ToolOutput) -> str:
        """
        formats outputs into janis tooldef string
        """
        self.update_output_selector_from_command(output)
        datatype = self.format_typestring(output.datatypes)
        tag = self.validate_tag(output.name)
        docstring = self.validate_docstring(output.help_text)
        selector = output.selector
        selector_contents = output.selector_contents

        # if selector is InputSelector, its referencing an input
        # that input tag will have been converted to a janis-friendly tag
        # same must be done to the selector contents
        if selector == 'InputSelector':
            selector_contents = self.validate_tag(selector_contents)        

        out_str = '\tToolToolOutput(\n'
        out_str += f'\t\t"{tag}",\n'

        if output.is_stdout:
            out_str += f'\t\tStdout({datatype}),\n'
        else:
            out_str += f'\t\t{datatype},\n'
            out_str += f'\t\tselector={selector}("{selector_contents}"),\n'
        
        out_str += f'\t\tdoc="{docstring}"\n'
        out_str += '\t),\n'

        return out_str


    def update_output_selector_from_command(self, output: ToolOutput) -> None:
        command = self.tool.command

        # is this a TODO? add logic incase of positional output? 
        # would be pretty weird 
        for positional in command.get_positionals():
            pass
        
        for option in command.get_options():
            for source in option.sources:
                if source.type == TokenType.GX_OUT:
                    if '$' + output.gx_var == source.gx_ref:
                        output.selector = 'InputSelector'
                        output.selector_contents = option.prefix.lstrip('-')



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




