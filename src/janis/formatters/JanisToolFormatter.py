

from command.components.outputs.RedirectOutput import RedirectOutput
from tool.Tool import Tool
from xmltool.ToolXMLMetadata import ToolXMLMetadata
from command.components.CommandComponent import CommandComponent
from command.components.inputs import Positional, Flag, Option
from janis.imports.ToolImportHandler import ToolImportHandler
import janis.snippets.tool_snippets as snippets
MISSING_CONTAINER_STRING = r'[NOTE] could not find a relevant container'


class JanisToolFormatter:
    def __init__(self, tool: Tool):
        self.tool = tool
        self.import_handler = ToolImportHandler()

    def to_janis_definition(self) -> str:
        str_note = self.format_top_note()
        str_path = self.format_path_appends()
        str_metadata = self.format_metadata()
        str_inputs = self.format_inputs()
        str_outputs = self.format_outputs()
        str_commandtool = self.format_commandtool()
        str_translate = self.format_translate_func() 
        str_imports = self.format_imports()
        return str_note + str_path + str_imports + str_metadata + str_inputs + str_outputs + str_commandtool + str_translate
    
    def format_top_note(self) -> str:
        metadata = self.tool.metadata
        return snippets.gxtool2janis_note_snippet(
            tool_name=metadata.id,
            tool_version=metadata.version
        )

    def format_path_appends(self) -> str:
        return snippets.path_append_snippet()
    
    def format_metadata(self) -> str:
        metadata = self.tool.metadata
        return snippets.metadata_snippet(
            description=metadata.description,
            version=metadata.version,
            help=metadata.help,
            wrapper_owner=metadata.owner,
            wrapper_creator=metadata.creator,
            doi=metadata.get_doi_citation(),
            url=metadata.url,
            citation=metadata.get_main_citation()
        )

    def format_inputs(self) -> str:
        inputs = self.tool.get_tags_inputs()
        out_str: str = ''
        positionals = {tag: x for tag, x in inputs.items() if isinstance(x, Positional)}
        flags = {tag: x for tag, x in inputs.items() if isinstance(x, Flag)}
        options = {tag: x for tag, x in inputs.items() if isinstance(x, Option)}

        out_str += 'inputs = ['
        out_str += '\n\t# Positionals'
        for tag, positional in positionals.items():
            self.import_handler.update(positional)
            out_str += f'{self.format_positional_input(tag, positional)},'

        out_str += '\n\t# Flags'
        for tag, flag in flags.items():
            self.import_handler.update(flag)
            out_str += f'{self.format_flag_input(tag, flag)},'
            
        out_str += '\n\t# Options'
        for tag, option in options.items():
            self.import_handler.update(option)
            out_str += f'{self.format_option_input(tag, option)},'
        out_str += '\n]\n'
        return out_str
   
    def format_positional_input(self, tag: str, positional: Positional) -> str:
        return snippets.tool_input_snippet(
            tag=tag,
            datatype=positional.get_janis_datatype_str(),
            position=positional.cmd_pos,
            doc=positional.get_docstring()
        )

    def format_flag_input(self, tag: str, flag: Flag) -> str:
        return snippets.tool_input_snippet(
            tag=tag,
            datatype=flag.get_janis_datatype_str(),
            position=flag.cmd_pos,
            prefix=flag.prefix,
            default=flag.get_default_value(),
            doc=flag.get_docstring()
        )
    
    def format_option_input(self, tag: str, opt: Option) -> str:
        default_value = self.get_wrapped_default_value(opt)
        return snippets.tool_input_snippet(
            tag=tag,
            datatype=opt.get_janis_datatype_str(),
            position=opt.cmd_pos,
            prefix=opt.prefix if opt.delim == ' ' else opt.prefix + opt.delim,
            kv_space=True if opt.delim == ' ' else False,
            default=default_value,
            doc=opt.get_docstring()
        )

    def get_wrapped_default_value(self, component: CommandComponent) -> str:
        default_value = component.get_default_value()
        if self.should_quote(component):
            return f'"{default_value}"'
        return default_value
    
    def should_quote(self, component: CommandComponent) -> bool:
        dclasses = [x.classname for x in component.janis_datatypes]
        if 'Int' in dclasses or 'Float' in dclasses:
            return False
        if component.get_default_value() is None:
            return False
        return True

    def format_outputs(self) -> str:
        outputs = self.tool.get_tags_outputs()
        out_str: str = ''
        out_str += 'outputs = ['

        for tag, output in outputs.items():
            self.import_handler.update(output)
            out_str += f'{self.format_output(tag, output)},'
        out_str += '\n]\n'

        return out_str

    def format_output(self, tag: str, output: CommandComponent) -> str:
        return snippets.tool_output_snippet(
            tag=tag,
            datatype=output.get_janis_datatype_str(),
            selector=output.get_selector_str() if not isinstance(output, RedirectOutput) else None, # type: ignore
            doc=output.get_docstring()
        )

    def format_commandtool(self) -> str:
        container = self.tool.container
        return snippets.command_tool_builder_snippet(
            toolname=self.tool.metadata.id,
            base_command=self.tool.base_command,
            container=container.url if container else MISSING_CONTAINER_STRING,
            version=self.tool.metadata.version, # should this be based on get_main_requirement()?
        )

    def format_translate_func(self) -> str:
        return snippets.translate_snippet(self.tool.metadata.id)

    def format_imports(self) -> str:
        return self.import_handler.imports_to_string()
        

