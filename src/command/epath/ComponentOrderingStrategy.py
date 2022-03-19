

from abc import ABC, abstractmethod
from command.components.CommandComponent import CommandComponent

from command.components.Flag import Flag
from command.components.Option import Option
from command.components.Positional import Positional


# def get_base_positionals(self) -> list[Positional]:
#     positionals = self.get_positionals()
#     positionals = [p for p in positionals if p.stage == 'pre_options']
#     return [p for p in positionals if not p.gxvar and p.has_single_value()]



class ComponentOrderingStrategy(ABC):
    @abstractmethod
    def annotate(self, components: list[CommandComponent]) -> list[CommandComponent]:
        """annotates components with command line positions"""
        ...

# TODO WTF epath cmd_pos orderings for components vs Command() orderings for components
class SimplifiedComponentOrderingStrategy(ComponentOrderingStrategy):
    def annotate(self, components: list[CommandComponent]) -> list[CommandComponent]:
        start_pos_count = self.count_starting_positionals(components)
        self.assign_positional_positions(components, start_pos_count)
        self.assign_flag_option_positions(components, start_pos_count)
        return components

    def count_starting_positionals(self, components: list[CommandComponent]) -> int:
        i: int = 0
        while i < len(components) and isinstance(components[i], Positional):
            i += 1
        return i 

    def assign_positional_positions(self, components: list[CommandComponent], start_pos_count: int) -> None:
        positionals = [c for c in components if isinstance(c, Positional)]
        for i, comp in enumerate(positionals):
            if i >= start_pos_count:
                comp.cmd_pos = i + 1
            else:
                comp.cmd_pos = i
                comp.before_opts = True

    def assign_flag_option_positions(self, components: list[CommandComponent], start_pos_count: int) -> None:
        options_flags = [c for c in components if isinstance(c, Option) or isinstance(c, Flag)]
        for comp in options_flags:
            comp.cmd_pos = start_pos_count


class RealisticComponentOrderingStrategy(ComponentOrderingStrategy):
    def annotate(self, components: list[CommandComponent]) -> list[CommandComponent]:
        # wayyy more complicated
        # 
        pos: int = 0
        for component in components:
            component.cmd_pos = pos
            if isinstance(component, Positional):
                pos += 1
        return components


