



from tool.tool_definition import GalaxyToolDefinition
from command.Command import Command
from command.cmdstr.CommandStatement import CommandStatement
from command.cmdstr.ToolExecutionString import ToolExecutionString

from command.components.CommandComponentFactory import CommandComponentFactory
from command.components.Flag import Flag
from command.components.Option import Option
from command.components.Positional import Positional

CommandComponent = Flag | Option | Positional


class CommandFactory:
    def __init__(self, tool: GalaxyToolDefinition):
        self.command = Command()
        self.cmdstrs: list[ToolExecutionString] = []
        self.component_factory = CommandComponentFactory(tool)
        self.has_non_xml_cmdstrs = False
        
        self.cmdstr_index: int = 0
        self.opts_encountered: bool = False
        self.positional_count: int = 0
        self.step_size: int = 1

    def create(self, command_line_strings: list[ToolExecutionString]) -> Command:
        self.refresh_attributes(command_line_strings)
        self.feed_cmdstrs(source='test')
        self.feed_cmdstrs(source='workflow')
        self.feed_cmdstrs(source='xml')
        self.cleanup()
        return self.command

    def refresh_attributes(self, command_line_strings: list[ToolExecutionString]) -> None:
        self.command = Command()
        self.has_non_xml_cmdstrs = True if any([cmdstr.source != 'xml' for cmdstr in command_line_strings]) else False
        self.cmdstrs = command_line_strings
        self.refresh_iter_attributes()

    def refresh_iter_attributes(self):
        self.command.positional_ptr = 0
        self.opts_encountered: bool = False
        self.step_size: int = 1

    def feed_cmdstrs(self, source: str) -> None:
        active_cmdstrs = [c for c in self.cmdstrs if c.source == source]
        for cmdstr in active_cmdstrs:
            self.feed(cmdstr)
    
    def feed(self, cmdstr: ToolExecutionString) -> None:
        self.refresh_iter_attributes()
        self.update_command(cmdstr)
        self.cmdstr_index += 1

    def update_command(self, cmdstr: ToolExecutionString) -> None:
        # flags and options first
        statement: CommandStatement = cmdstr.tool_statement
        self.update_command_components(statement, disallow=[Positional])
        # positionals if test or workflowstep (or only xml available)
        #if cmdstr.source != 'xml' or not self.has_non_xml_cmdstrs:
        self.update_command_components(statement, disallow=[Flag, Option])
    
    def update_command_components(self, cmdstmt: CommandStatement, disallow: list[type[CommandComponent]]) -> None:
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
            components = self.component_factory.create(cword, nword, self.cmdstr_index)
            components = self.refine_components(components)
            self.update_step_size(components)
            self.update_components(components, disallow=disallow)
            i += self.step_size
    
    def refine_components(self, components: list[CommandComponent]) -> list[CommandComponent]:
        # refines each component and returns
        return [self.refine_comp(comp) for comp in components]
    
    def refine_comp(self, component: CommandComponent) -> CommandComponent:
        """
        updates the component based on existing knowledge of the command.
        and example is where we think a component was an option, 
        but its actually a flag followed by a positional.
        """
        # cast Option to Flag
        if isinstance(component, Option):
            flags = self.command.get_flags()
            for flag in flags:
                match flag:
                    case Flag(prefix=component.prefix):
                        component = self.component_factory.cast_to_flag(component)
                        break
                    case _:
                        pass
        return component

    def update_step_size(self, components: list[CommandComponent]) -> None:
        # TODO lol edge cases are so complicated.
        # should cover 99% of cases with the current implementation
        if len(components) == 1 and isinstance(components[0], Option):
            self.step_size = 2
        else:
            self.step_size = 1

    def update_components(self, components: list[CommandComponent], disallow: list[type[CommandComponent]]) -> None:
        for component in components:
            if type(component) not in disallow:
                self.command.update(component)
    
    def cleanup(self) -> None:
        self.update_components_presence_array()

    def update_components_presence_array(self) -> None:
        for component in self.command.get_all_components():
            component.update_presence_array(self.cmdstr_index)


