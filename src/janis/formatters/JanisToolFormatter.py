


from typing import Optional
from command.components.outputs.RedirectOutput import RedirectOutput
from xmltool.ToolXMLMetadata import ToolXMLMetadata
from containers.Container import Container
from command.components.CommandComponent import CommandComponent
from command.components.inputs import Positional, Flag, Option
from janis.imports.ImportHandler import ImportHandler
import janis.snippets.tool_snippets as snippets
MISSING_CONTAINER_STRING = r'[NOTE] could not find a relevant container'


class JanisToolFormatter:
    def __init__(self):
        self.import_handler = ImportHandler()

    def format_top_note(self, metadata: ToolXMLMetadata) -> str:
        return snippets.gxtool2janis_note_snippet(
            tool_name=metadata.id,
            tool_version=metadata.version
        )

    def format_path_appends(self) -> str:
        return snippets.path_append_snippet()
    
    def format_metadata(self, metadata: ToolXMLMetadata) -> str:
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

    def format_inputs(self, inputs: list[CommandComponent]) -> str:
        positionals = [x for x in inputs if isinstance(x, Positional)]
        flags = [x for x in inputs if isinstance(x, Flag)]
        options = [x for x in inputs if isinstance(x, Option)]

        out_str: str = ''
        out_str += 'inputs = ['
        out_str += '\n\t# Positionals'
        for positional in positionals:
            self.import_handler.update(positional)
            out_str += f'{self.format_positional_input(positional)},'

        out_str += '\n\t# Flags'
        for flag in flags:
            self.import_handler.update(flag)
            out_str += f'{self.format_flag_input(flag)},'
            
        out_str += '\n\t# Options'
        for option in options:
            self.import_handler.update(option)
            out_str += f'{self.format_option_input(option)},'
        out_str += '\n]\n'
        return out_str
   
    def format_positional_input(self, positional: Positional) -> str:
        return snippets.tool_input_snippet(
            tag=positional.get_janis_tag(),
            datatype=positional.get_janis_datatype_str(),
            position=positional.cmd_pos,
            doc=positional.get_docstring()
        )

    def format_flag_input(self, flag: Flag) -> str:
        return snippets.tool_input_snippet(
            tag=flag.get_janis_tag(),
            datatype=flag.get_janis_datatype_str(),
            position=flag.cmd_pos,
            prefix=flag.prefix,
            doc=flag.get_docstring()
        )
    
    def format_option_input(self, opt: Option) -> str:
        default_value = self.get_wrapped_default_value(opt)
        return snippets.tool_input_snippet(
            tag=opt.get_janis_tag(),
            datatype=opt.get_janis_datatype_str(),
            position=opt.cmd_pos,
            prefix=opt.prefix if opt.delim == ' ' else opt.prefix + opt.delim,
            kv_space=True if opt.delim == ' ' else False,
            default=default_value,
            doc=opt.get_docstring()
        )

    def get_wrapped_default_value(self, component: CommandComponent) -> str:
        dclasses = [x.classname for x in component.datatypes]
        should_quote = False if 'Int' in dclasses or 'Float' in dclasses else True
        default_value = component.get_default_value()
        if should_quote:
            return f'"{default_value}"'
        return default_value

    def format_outputs(self, outputs: list[CommandComponent]) -> str:
        out_str: str = ''
        out_str += 'outputs = ['

        for output in outputs:
            self.import_handler.update(output)
            out_str += f'{self.format_output(output)},'
        out_str += '\n]\n'

        return out_str

    def format_output(self, output: CommandComponent) -> str:
        return snippets.tool_output_snippet(
            tag=output.get_janis_tag(),
            datatype=output.get_janis_datatype_str(),
            selector=output.get_selector_str() if not isinstance(output, RedirectOutput) else None, # type: ignore
            doc=output.get_docstring()
        )

    def format_commandtool(self, metadata: ToolXMLMetadata, base_command: list[str], container: Optional[Container]) -> str:
        return snippets.command_tool_builder_snippet(
            toolname=metadata.id,
            base_command=base_command,
            container=container.url if container else MISSING_CONTAINER_STRING,
            version=metadata.version, # should this be based on get_main_requirement()?
        )

    def format_translate_func(self, metadata: ToolXMLMetadata) -> str:
        return snippets.translate_snippet(metadata.id)

    def format_imports(self) -> str:
        return self.import_handler.imports_to_string()
        

