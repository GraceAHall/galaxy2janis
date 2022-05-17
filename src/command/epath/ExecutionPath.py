

from dataclasses import dataclass
from typing import Optional

from command.components.CommandComponent import CommandComponent
from command.components.linux.StreamMerge import StreamMerge
from command.components.linux.Tee import Tee
from command.epath.ComponentOrderingStrategy import SimplifiedComponentOrderingStrategy
from command.tokens.Tokens import Token
import command.tokens.utils as utils



@dataclass
class EPathPosition:
    ptr: int
    token: Token
    ignore: bool = False
    component: Optional[CommandComponent] = None


class ExecutionPath:
    id: int

    def __init__(self, tokens: list[Token]):
        self.positions: list[EPathPosition] = self._init_positions(tokens)
        self.tokens_to_excise: list[int] = []

    def get_components(self) -> list[CommandComponent]:
        components = self._get_component_list()
        ordering_strategy = SimplifiedComponentOrderingStrategy()
        return ordering_strategy.order(components)
    
    def _get_component_list(self) -> list[CommandComponent]:
        """
        gets the CommandComponents in this EPath (unique)
        preserves ordering
        """
        ignore = [Tee, StreamMerge]
        out: list[CommandComponent] = []
        for position in self.positions:
            if position.component and type(position.component) not in ignore and position.component not in out:
                out.append(position.component)
        return out
    
    def _init_positions(self, tokens: list[Token]) -> list[EPathPosition]:
        positions = [EPathPosition(i, token) for i, token in enumerate(tokens)]
        end_sentinel = utils.spawn_end_sentinel()
        positions.append(EPathPosition(len(positions), end_sentinel))
        return positions

    def __str__(self) -> str:
        out: str = '\n'
        for position in self.positions:
            out += f'{str(position.ptr):<3}{position.token.text[:39]:<40}{position.token.type:<35}\n'
        return out


