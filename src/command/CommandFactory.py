



from command.Command import Command
from command.cmdstr.CommandStatement import CommandStatement
from command.cmdstr.ToolExecutionString import ToolExecutionString
from command.components.CommandComponent import CommandComponent
from command.components.CommandComponentFactory import CommandComponentFactory
from command.components.Positional import Positional
from command.components.Option import Option
from tool.tool_definition import GalaxyToolDefinition


class CommandFactory:
    def __init__(self, tool: GalaxyToolDefinition):
        self.command = Command()
        self.cmdstrs: list[ToolExecutionString] = []
        self.component_factory = CommandComponentFactory(tool)
        self.has_non_xml_cmdstrs = False
        
        self.ingested_cmdstr_index: int = 0
        self.opts_encountered: bool = False
        self.positional_count: int = 0
        self.step_size: int = 1

    def create(self, command_line_strings: list[ToolExecutionString]) -> Command:
        self.refresh_attributes(command_line_strings)
        self.feed_cmdstrs(source='test')
        self.feed_cmdstrs(source='workflow')
        self.feed_cmdstrs(source='xml')
        self.cleanup()

    def refresh_attributes(self, command_line_strings: list[ToolExecutionString]) -> None:
        self.command = Command()
        self.has_non_xml_cmdstrs = True if any([cmdstr.source != 'xml' for cmdstr in command_line_strings]) else False
        self.cmdstrs = command_line_strings
        self.num_ingested_cmdstrs = 0   
        self.refresh_iter_attributes()

    def refresh_iter_attributes(self):
        self.opts_encountered: bool = False
        self.positional_count: int = 0
        self.step_size: int = 1

    def feed_cmdstrs(self, source: str) -> None:
        active_cmdstrs = [c for c in self.cmdstrs if c.source == source]
        for cmdstr in active_cmdstrs:
            self.feed(cmdstr)
    
    def feed(self, cmdstr: ToolExecutionString) -> None:
        self.ingested_cmdstr_index += 1
        self.refresh_iter_attributes()
        self.update_command(cmdstr)

    def update_command(self, cmdstr: ToolExecutionString) -> None:
        # flags and options first
        statement: CommandStatement = cmdstr.tool_statement
        self.update_flags_options(statement)
        # positionals if test or workflowstep (or only xml available)
        if cmdstr.source != 'xml' or not self.has_non_xml_cmdstrs:
            self.update_positionals(statement)
    
    def update_flags_options(self, cmdstmt: CommandStatement) -> None:
        """
        iterate through command words (with next word for context)
        each pair of words may actually yield more than one component.
        see emboss_pepinfo.xml - has option value="-generalplot yes -hydropathyplot no"
        it is usually a single component though. only when is galaxy param.
        """
        i = 0
        while i < len(cmdstmt.cmdwords) - 1:
            self.step_size = 1
            cword = cmdstmt.cmdwords[i]
            nword = cmdstmt.cmdwords[i + 1]
            components = self.component_factory.create(cword, nword)
            components = self.refine_components(components)
            self.update_step_size(components)
            self.update_components(components, disallow=[Positional])
            i += self.step_size
    
    def refine_components(self, components: list[CommandComponent]) -> list[CommandComponent]:
        """
        updates the component based on existing knowledge of the command.
        and example is where we think a component was an option, 
        but its actually a flag followed by a positional.
        """
        # get Command to look up its components and see if any match or part match
        # cast Option to 
        raise NotImplementedError
    
    def refine_comp(self, component: CommandComponent) -> CommandComponent:
        raise NotImplementedError

    def update_step_size(self, components: list[CommandComponent]) -> None:
        raise NotImplementedError
        if isinstance(component, Option):
            self.step_size = 2
        else:
            self.step_size = 1

    def update_components(self, components: list[CommandComponent], disallow: list[CommandComponent]) -> None:
        raise NotImplementedError
    
    def update_positionals(self, cmdstmt: CommandStatement) -> None:
        raise NotImplementedError

    def cleanup(self) -> None:
        self.update_components_presence_array() # ?????


