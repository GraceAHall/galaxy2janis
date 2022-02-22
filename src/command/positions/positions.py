


from typing import Tuple
from command.components.CommandComponent import CommandComponent
from .PositionResolver import PositionResolver

def format_input_positions(components: list[CommandComponent]) -> list[Tuple[int, CommandComponent]]:
    pa = PositionResolver(components)
    out = pa.resolve()
    return out
