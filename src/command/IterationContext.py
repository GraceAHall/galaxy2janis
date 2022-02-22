

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from command.CommandFactory import CommandFactory

from dataclasses import dataclass

from command.components.Option import Option
from command.components.Positional import Positional
from command.components.CommandComponent import CommandComponent


@dataclass
class IterationContext:
    """
    this class provides control over updating and getting position of which 
    cmdstr is being fed, and which position we are throughout that cmdstr
    there only is a single instance of this class created, which is passed through 
    other classess and functions to provide a single source of truth
    ONLY A COMMANDFACTORY() IS ALLOWED TO UPDATE AN INSTANCE OF THIS CLASS
    """
    cmdstr: int = 0
    position: int = 0
    step_size: int = 1

    def increment_cmdstr(self):
        self.cmdstr += 1
        self.position = 0
        self.step_size = 1
        self.opts_encountered = False

    def update(self, valid_components: list[CommandComponent], referrer: CommandFactory) -> None:
        self.update_step(valid_components)
        self.update_position(valid_components)

    def update_step(self, components: list[CommandComponent]) -> None:
        if all([isinstance(comp, Option) for comp in components]):
            self.step_size = 2
        else:
            self.step_size = 1

    def update_position(self, components: list[CommandComponent]) -> None:
        if len(components) == 1 and isinstance(components[0], Positional):
            self.position += 1
