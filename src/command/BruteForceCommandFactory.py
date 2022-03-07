

from command.IterationContext import IterationContext

from command.Command import Command

from tool.tool_definition import GalaxyToolDefinition
from command.cmdstr.DynamicCommandString import DynamicCommandString

from command.cmdstr.ExecutionPath import ExecutionPath
from command.iteration.GreedyEPathIterator import GreedyEPathIterator

from command.components.Flag import Flag
from command.components.Option import Option
from command.components.Positional import Positional
from command.components.CommandComponent import CommandComponent
import command.iteration.utils as component_utils

class BruteForceCommandFactory:
    epath_iterator: GreedyEPathIterator
    
    def __init__(self, tool: GalaxyToolDefinition):
        self.tool = tool
        self.command = Command()
        self.iter_context = IterationContext()
        self.cmdstrs: list[DynamicCommandString] = []
        self.has_non_xml_sources = False

    def create(self, cmdstrs: list[DynamicCommandString]) -> Command:
        self.set_attrs(cmdstrs)
        self.feed_cmdstrs(source='xml')
        self.feed_cmdstrs(source='test')
        self.feed_cmdstrs(source='workflow')
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
                epath.id = self.iter_context.epath
                self.feed(epath)

    def feed(self, epath: ExecutionPath) -> None:
        self.command.pos_manager.reset()
        self.update_redirects(epath)
        self.infer_components_via_param_args(epath)
        self.infer_components_via_iter_epath(epath)
        self.iter_context.increment_epath()

    def update_redirects(self, epath: ExecutionPath) -> None:
        if epath.redirect:
            self.update_command_components(epath.redirect)

    def infer_components_via_param_args(self, epath: ExecutionPath) -> None:
        iterator = GreedyEPathIterator(epath)
        for param in self.tool.list_inputs():
            if param.argument:
                component = iterator.search(param.argument)
                if component:
                    self.update_command_components(component)
    
    def infer_components_via_iter_epath(self, epath: ExecutionPath) -> None:
        iterator = GreedyEPathIterator(epath)
        for component in iterator.iter():
            self.update_command_components(component)
    
    def update_command_components(self, component: CommandComponent) -> None:
        component = self.refine_component(component)
        self.iter_context.update(component)
        self.annotate_iter_attrs(component)
        self.command.update(component)
    
    def refine_component(self, component: CommandComponent) -> CommandComponent:
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
                        component = component_utils.cast_opt_to_flag(component)
                        break
                    case _:
                        pass
        return component
    
    def annotate_iter_attrs(self, component: CommandComponent) -> None:
        match component:
            case Positional():
                component.cmd_pos = self.iter_context.positional_count
                component.update_presence_array(self.iter_context.epath)
            case _:
                component.update_presence_array(self.iter_context.epath)
   
    def cleanup(self) -> None:
        self.update_components_presence_array()

    def update_components_presence_array(self) -> None:
        for component in self.command.get_inputs():
            component.update_presence_array(self.iter_context.epath - 1, fill_false=True)


