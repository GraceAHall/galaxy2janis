

from command.IterationContext import IterationContext

from command.Command import Command

from tool.tool_definition import GalaxyToolDefinition
from command.cmdstr.DynamicCommandString import DynamicCommandString

from command.epath.ExecutionPath import ExecutionPath
from command.epath.GreedyEPathAnnotator import GreedyEPathAnnotator
#from command.epath.TwoWordEPathAnnotator import TwoWordEPathAnnotator

from command.components.creation.CommandComponentFactory import CommandComponentFactory
from command.components.Flag import Flag
from command.components.Option import Option
from command.components.Positional import Positional
from command.components.CommandComponent import CommandComponent

# deprecated oops
class CommandFactory:
    epath_iterator: GreedyEPathAnnotator
    
    def __init__(self, tool: GalaxyToolDefinition):
        self.tool = tool
        self.command = Command()
        self.iter_context = IterationContext()
        self.cmdstrs: list[DynamicCommandString] = []
        self.component_factory = CommandComponentFactory(tool)
        self.has_non_xml_sources = False

    def create(self, cmdstrs: list[DynamicCommandString]) -> Command:
        self.set_attrs(cmdstrs)
        self.feed_cmdstrs(source='test')
        self.feed_cmdstrs(source='workflow')
        self.feed_cmdstrs(source='xml')
        self.cleanup()
        return self.command

    def set_attrs(self, cmdstrs: list[DynamicCommandString]) -> None:
        self.command = Command()
        self.has_non_xml_sources = True if any([source.source != 'xml' for source in cmdstrs]) else False
        self.cmdstrs = cmdstrs

    def feed_cmdstrs(self, source: str) -> None:
        active_cmdstrs = [c for c in self.cmdstrs if c.source == source]
        for cmdstr in active_cmdstrs:
            for epath in cmdstr.tool_statement.get_execution_paths():
                self.feed(epath)

    def feed(self, epath: ExecutionPath) -> None:
        self.command.pos_manager.reset()
        self.update_redirects(epath)
        self.infer_components_using_param_arguments(epath)
        self.update_command_components(epath)
        self.iter_context.increment_cmdstr()

    def infer_components_using_param_arguments(self, epath: ExecutionPath) -> None:
        iterator = GreedyEPathAnnotator(epath)
        for param in self.tool.list_inputs():
            if param.argument:
                component = iterator.search(param.argument)
                if component:
                    pass
    
    def update_redirects(self, epath: ExecutionPath) -> None:
        if epath.redirect:
            self.update_command([epath.redirect])
    
    def update_command_components(self, cmdstmt: ExecutionPath, disallow: list[type[CommandComponent]]=[]) -> None:
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


