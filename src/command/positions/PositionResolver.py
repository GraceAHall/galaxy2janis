



from typing import Tuple
from command.components.CommandComponent import CommandComponent
from command.components.Flag import Flag
from command.components.Option import Option
from command.components.Positional import Positional

class PositionResolver:
    def __init__(self, components: list[CommandComponent]):
        self.components = components
        self.base_command_items: int = 0

    def get_positionals(self) -> list[Positional]:
        """returns positionals sorted by cmd_pos"""
        positionals = [c for c in self.components if isinstance(c, Positional)]
        positionals.sort(key=lambda x: x.cmd_pos)
        return positionals
    
    def get_flags_opts(self) -> list[CommandComponent]:
        """returns flags and options"""
        return [c for c in self.components if isinstance(c, Flag) or isinstance(c, Option)]
    
    def get_base_positionals(self) -> list[Positional]:
        positionals = self.get_positionals()
        positionals = [p for p in positionals if p.stage == 'pre_options']
        return [p for p in positionals if not p.gxvar and p.has_single_value()]

    def get_pre_opts_positionals(self) -> list[Positional]:
        positionals = self.get_positionals()
        positionals = [p for p in positionals if p.stage == 'pre_options']
        return [p for p in positionals if p.gxvar or not p.has_single_value()]

    def get_post_opts_positionals(self) -> list[Positional]:
        positionals = self.get_positionals()
        positionals = [p for p in positionals if p.stage == 'post_options']
        return positionals

    def resolve(self) -> list[Tuple[int, CommandComponent]]:
        pos: int = 0
        out: list[Tuple[int, CommandComponent]] = []
        
        # base command positionals = 0
        for positional in self.get_base_positionals():
            out.append((pos, positional))
        
        # pre options positionals = 1-X 
        for positional in self.get_pre_opts_positionals():
            pos += 1
            out.append((pos, positional))

        # in options flags/options = X+1
        pos += 1
        for comp in self.get_flags_opts():
            out.append((pos, comp))
        
        for positional in self.get_post_opts_positionals():
            pos += 1
            out.append((pos, positional))
        
        return out