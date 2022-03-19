


from typing import Optional

from xmltool.param.Param import Param
from xmltool.tool_definition import XMLToolDefinition
from containers.Container import Container

from command.infer import Command
from command.components.CommandComponent import CommandComponent
from command.components.linux_constructs import Redirect
from command.components.Flag import Flag
from command.components.Option import Option
from command.components.Positional import Positional

from datatypes.DatatypeRegister import DatatypeRegister
from janis_definition.ImportHandler import ImportHandler
from command.components.TagFormatter import TagFormatter
from xmltool.parsing.selectors import Selector, SelectorType

from janis_definition.formatting_snippets import (
    path_append_snippet,
    tool_input_snippet,
    tool_output_snippet,
    command_tool_builder_snippet,
    translate_snippet
)

selector_map: dict[SelectorType, str] = {
    SelectorType.INPUT_SELECTOR: 'InputSelector',
    SelectorType.WILDCARD_SELECTOR: 'WildcardSelector',
    SelectorType.STRING_FORMATTER: 'StringFormatter'
}


class JanisFormatter:
    def __init__(self):
        self.datatype_formatter = DatatypeRegister()
        self.tag_formatter = TagFormatter()
        self.import_handler = ImportHandler(self.datatype_formatter)

    def format_path_appends(self) -> str:
        return path_append_snippet

    # TODO refactor
    def format_inputs(self, command: Command) -> str:
        components = command.get_component_positions()
        out_str: str = ''
        out_str += 'inputs = ['

        out_str += '\n\t# Positionals'
        for cmd_pos, positional in components['positionals']:
            self.import_handler.update(positional)
            out_str += f'{self.format_positional(cmd_pos, positional)},'

        out_str += '\n\t# Flags'
        for cmd_pos, flag in components['flags']:
            self.import_handler.update(flag)
            out_str += f'{self.format_flag(cmd_pos, flag)},'
            
        out_str += '\n\t# Options'
        for cmd_pos, option in components['options']:
            self.import_handler.update(option)
            out_str += f'{self.format_option(cmd_pos, option)},'
        out_str += '\n]'
        return out_str
   
    def format_positional(self, pos: int, positional: Positional) -> str:
        tag = self.tag_formatter.format(positional.get_name(), positional.get_datatype()[0])
        datatype = self.datatype_formatter.get(component=positional)
        return tool_input_snippet(
            tag=tag,
            datatype=datatype,
            position=pos,
            doc=positional.get_docstring()
        )

    def format_flag(self, pos: int, flag: Flag) -> str:
        datatype = self.datatype_formatter.get(component=flag)
        return tool_input_snippet(
            tag=self.tag_formatter.format(flag.prefix, flag.get_datatype()[0]),
            datatype=datatype,
            position=pos,
            prefix=flag.prefix,
            doc=flag.get_docstring()
        )
    
    def format_option(self, pos: int, opt: Option) -> str:
        datatype = self.datatype_formatter.get(component=opt)
        default = opt.get_default_value()
        if default:
            if 'Int' not in datatype and 'Float' not in datatype:
                default = f'"{default}"'
        return tool_input_snippet(
            tag=self.tag_formatter.format(opt.prefix, opt.get_datatype()[0]),
            datatype=datatype,
            position=pos,
            prefix=opt.prefix if opt.delim == ' ' else opt.prefix + opt.delim,
            kv_space=True if opt.delim == ' ' else False,
            default=default,
            doc=opt.get_docstring()
        )

    def format_outputs(self, xmltool: XMLToolDefinition, command: Command) -> str:
        out_str: str = ''
        out_str += 'outputs = ['

        command_outputs = command.get_outputs()
        command_output_param_names = [o.gxvar.name for o in command_outputs if o.gxvar]
        tool_output_params = [out for out in xmltool.list_outputs() if out.name not in command_output_param_names]
        # TODO FIX THIS AWFUL OUTPUT SHIT
        # galaxy outputs with no reference in <command> section
        # usually use 'from_work_dir' to get file(s)
        for output in tool_output_params:
            self.import_handler.update(output)
            out_str += f'{self.format_output_param(output)},'
        # Redirects and command components linked to galaxy outputs
        for output in command_outputs:
            self.import_handler.update(output)
            out_str += f'{self.format_output_component(output)},'
        out_str += '\n]'
        return out_str

    def format_output_param(self, param: Param) -> str:
        name = self.tag_formatter.format(param.name, param.datatypes[0])
        datatype = self.datatype_formatter.get(param=param)
        stype: Optional[str] = None
        scontents: Optional[str] = None
        if param.selector:
            stype = selector_map[param.selector.stype]
            scontents = param.selector.contents
        return tool_output_snippet(
            tag=name,
            datatype=datatype,
            selector_type=stype,
            selector_contents=scontents,
            doc=param.get_docstring()
        )

    def format_output_component(self, component: CommandComponent) -> str:
        datatype = self.datatype_formatter.get(component=component)
        name = self.format_output_name(component)
        selector = self.format_selector(component, name)
        stype: Optional[str] = None
        scontents: Optional[str] = None
        if selector:
            stype = selector_map[selector.stype]
            scontents = selector.contents
        return tool_output_snippet(
            tag=name,
            datatype=datatype,
            selector_type=stype,
            selector_contents=scontents,
            doc=component.get_docstring()
        )
        
    def format_output_name(self, component: CommandComponent) -> str:
        name: str = ''
        match component:
            case Flag() | Option():
                name = component.prefix  
            case Positional() | Redirect():
                name = component.get_name()  
            case _:
                pass
        return self.tag_formatter.format(name, component.get_datatype()[0])

    def format_selector(self, component: CommandComponent, output_name: str) -> Optional[Selector]:
        if not isinstance(component, Redirect):
            return Selector(
                stype=SelectorType.INPUT_SELECTOR,
                contents=output_name
            )
        return None

    def format_commandtool(self, xmltool: XMLToolDefinition, command: Command, container: Container) -> str:
        base_positionals = command.get_base_positionals()
        base_command = [p.get_default_value() for p in base_positionals]
        name: str = xmltool.metadata.id

        return command_tool_builder_snippet(
            toolname=name,
            base_command=base_command,
            container=container.url,
            version=xmltool.metadata.version, # should this be based on get_main_requirement()?
            help=xmltool.metadata.help
        )

    def format_translate_func(self, xmltool: XMLToolDefinition) -> str:
        name: str = xmltool.metadata.id
        return translate_snippet(name)

    def format_imports(self) -> str:
        return self.import_handler.imports_to_string()
        

