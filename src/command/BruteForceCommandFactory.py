

from command.IterationContext import IterationContext

from command.Command import Command

from tool.tool_definition import GalaxyToolDefinition
from command.cmdstr.CommandStatement import CommandStatement
from command.cmdstr.ToolExecutionSource import ToolExecutionSource

from command.components.creation.CommandComponentFactory import CommandComponentFactory
from command.components.Flag import Flag
from command.components.Option import Option
from command.components.Positional import Positional
from command.components.CommandComponent import CommandComponent
from command.iterators.GreedyCmdStrIterator import GreedyCmdStrIterator


class BruteForceCommandFactory:
    def __init__(self, tool: GalaxyToolDefinition):
        self.command = Command()
        self.cmdstrs: list[ToolExecutionSource] = []
        self.iter_context = IterationContext()
        self.cmdstr_iterator: GreedyCmdStrIterator = GreedyCmdStrIterator()
        self.component_factory = CommandComponentFactory(tool)
        self.has_non_xml_cmdstrs = False

    def create(self, command_line_strings: list[ToolExecutionSource]) -> Command:
        self.set_attrs(command_line_strings)
        self.ingest_test_cmdstrs()
        #self.ingest_workflow_cmdstrs()
        self.ingest_xml_cmdstrs()
        self.cleanup()
        return self.command

    def set_attrs(self, command_line_strings: list[ToolExecutionSource]) -> None:
        self.command = Command()
        self.has_non_xml_cmdstrs = True if any([cmdstr.source != 'xml' for cmdstr in command_line_strings]) else False
        self.cmdstrs = command_line_strings

    def ingest_test_cmdstrs(self) -> None:
        test_cmdstrs = [c for c in self.cmdstrs if c.source == 'test']
        for cmdstr in test_cmdstrs:
            self.feed(cmdstr)
    
    def ingest_workflow_cmdstrs(self) -> None:
        test_cmdstrs = [c for c in self.cmdstrs if c.source == 'workflow']
        for cmdstr in test_cmdstrs:
            self.feed(cmdstr)
    
    def ingest_xml_cmdstrs(self) -> None:
        xml_cmdstr = [c for c in self.cmdstrs if c.source == 'xml'][0]
        for exe_path in gen_execution_paths(xml_cmdstr):
            self.feed(exe_path)

    def feed(self, cmdstr: ToolExecutionSource) -> None:
        self.command.pos_manager.reset()
        statement: CommandStatement = cmdstr.tool_statement
        self.update_redirects(statement)
        self.update_components_from_params()
        self.update_components_from_iteration(statement)
        self.iter_context.increment_cmdstr()

    def update_redirects(self, cmdstmt: CommandStatement) -> None:
        if cmdstmt.redirect:
            self.update_command([cmdstmt.redirect])

    def update_components_from_params(self) -> None:
        pass
    
    def update_components_from_iteration(self, cmdstmt: CommandStatement, disallow: list[type[CommandComponent]]=[]) -> None:
        """
        iterate through command words (with next word for context)
        each pair of words may actually yield more than one component.
        see emboss_pepinfo.xml - has option value="-generalplot yes -hydropathyplot no"
        it is usually a single component though. only when is galaxy param.
        """
        cmdstr_components: list[CommandComponent] = []
        i = 0
        while i < len(cmdstmt.cmdwords) - 1:
            cword = cmdstmt.cmdwords[i]
            nword = cmdstmt.cmdwords[i + 1]
            components = self.component_factory.create(cword, nword)
            components = self.refine_components(components)
            self.iter_context.update(components, referrer=self)
            components = self.filter_components(components, disallow=disallow)
            components = self.annotate_iter_attrs(components)
            cmdstr_components += components
            i += self.iter_context.step_size
        self.update_command(cmdstr_components)
    
    def annotate_iter_attrs(self, components: list[CommandComponent]) -> list[CommandComponent]:
        for comp in components:
            match comp:
                case Positional():
                    comp.cmd_pos = self.iter_context.position
                    comp.update_presence_array(self.iter_context.cmdstr)
                case _:
                    comp.update_presence_array(self.iter_context.cmdstr)
        return components

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

    def filter_components(self, components: list[CommandComponent], disallow: list[type[CommandComponent]]) -> list[CommandComponent]:
        return [comp for comp in components if type(comp) not in disallow]

    def update_command(self, components: list[CommandComponent]) -> None:
        for comp in components:
            self.command.update(comp)
    
    def cleanup(self) -> None:
        self.update_components_presence_array()

    def update_components_presence_array(self) -> None:
        for component in self.command.get_inputs():
            component.update_presence_array(self.iter_context.cmdstr - 1, fill_false=True)


