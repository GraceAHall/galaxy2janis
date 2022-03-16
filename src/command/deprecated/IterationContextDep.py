

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from command.deprecated.CommandFactoryDep import CommandFactory

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
    """
    epath_count: int = 0
    positional_count: int = 0
    #step_size: int = 1

    def increment_epath(self):
        self.epath_count += 1
        self.positional_count = 0
        #self.step_size = 1
        self.opts_encountered = False

    def update(self, component: CommandComponent) -> None:
        #self.update_step(valid_components)
        self.update_position(component)

    def update_position(self, component: CommandComponent) -> None:
        if isinstance(component, Positional):
            self.positional_count += 1

    # def update_step(self, components: list[CommandComponent]) -> None:
    #     if all([isinstance(comp, Option) for comp in components]):
    #         self.step_size = 2
    #     else:
    #         self.step_size = 1

