

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Optional, Callable, Tuple

from command.positions.PositionManager import PositionManager
from command.components.Positional import Positional
from command.components.Flag import Flag
from command.components.Option import Option
from command.components.linux_constructs import Redirect
from command.components.CommandComponent import CommandComponent
from tool.param.OutputParam import OutputParam
from command.positions.positions import format_input_positions
from tool.param.Param import Param

class Updater(ABC):

    @abstractmethod
    def update(self, command: Command, pos_manager: PositionManager, incoming: Any) -> None:
        """updates the command's store of CommandComponents with the incoming component"""
        ...

    @abstractmethod
    def should_merge(self) -> bool:
        """determines whether to merge the incoming CommandComponent with an existing one, or add new"""
        ...
    
    @abstractmethod
    def merge(self) -> None:
        """updates via merging the incoming CommandComponent with a known CommandComponent"""
        ...
    
    @abstractmethod
    def add(self) -> None:
        """updates via adding a new CommandComponent"""
        ...


class PositionalUpdater(Updater):
    command: Command
    incoming: Positional

    def update(self, command: Command, pos_manager: PositionManager, incoming: Positional) -> None:
        self.command = command
        self.incoming = incoming
        self.update_position_info(pos_manager)
        if self.should_merge():
            self.merge()
        else:
            self.add()
    
    def update_position_info(self, pos_manager: PositionManager) -> None:
        pos_manager.update('positional')
        pos_manager.mark_component_stage(self.incoming)

    def should_merge(self) -> bool:
        cmd_pos = self.incoming.cmd_pos
        existing_comp = self.command.get_positional(cmd_pos)
        if existing_comp:
            return True
        return False
    
    def merge(self) -> None:
        cmd_pos = self.incoming.cmd_pos
        existing_comp = self.command.get_positional(cmd_pos)
        if existing_comp:
            existing_comp.update(self.incoming)
    
    def add(self) -> None:
        cmd_pos = self.incoming.cmd_pos
        self.command.positionals[cmd_pos] = self.incoming


class FlagUpdater(Updater):
    command: Command
    incoming: Flag

    def update(self, command: Command, pos_manager: PositionManager, incoming: Flag) -> None:
        self.command = command
        self.incoming = incoming
        self.update_position_info(pos_manager)
        if self.should_merge():
            self.merge()
        else:
            self.add()

    def update_position_info(self, pos_manager: PositionManager) -> None:
        pos_manager.update('flag')
        pos_manager.mark_component_stage(self.incoming)

    def should_merge(self) -> bool:
        query_prefix = self.incoming.prefix
        existing_comp = self.command.get_flag(query_prefix)
        if existing_comp:
            return True
        return False
    
    def merge(self) -> None:
        query_prefix = self.incoming.prefix
        existing_comp = self.command.get_flag(query_prefix)
        if existing_comp:
            existing_comp.update(self.incoming)
    
    def add(self) -> None:
        prefix = self.incoming.prefix
        self.command.flags[prefix] = self.incoming


class OptionUpdater(Updater):
    command: Command
    incoming: Option

    def update(self, command: Command, pos_manager: PositionManager, incoming: Option) -> None:
        self.command = command
        self.incoming = incoming
        self.update_position_info(pos_manager)
        if self.should_merge():
            self.merge()
        else:
            self.add()

    def update_position_info(self, pos_manager: PositionManager) -> None:
        pos_manager.update('option')
        pos_manager.mark_component_stage(self.incoming)

    def should_merge(self) -> bool:
        query_prefix = self.incoming.prefix
        existing_comp = self.command.get_option(query_prefix)
        if existing_comp:
            return True
        return False
    
    def merge(self) -> None:
        query_prefix = self.incoming.prefix
        existing_comp = self.command.get_option(query_prefix)
        if existing_comp:
            existing_comp.update(self.incoming)
    
    def add(self) -> None:
        prefix = self.incoming.prefix
        self.command.options[prefix] = self.incoming


class RedirectUpdater(Updater):
    command: Command
    incoming: Redirect

    def update(self, command: Command, pos_manager: PositionManager, incoming: Redirect) -> None:
        self.command = command
        self.incoming = incoming
        if self.should_merge():
            self.merge()
        else:
            self.add()

    def should_merge(self) -> bool:
        if self.command.redirect:
            return True
        return False
    
    def merge(self) -> None:
        if self.command.redirect:
            self.command.redirect.update(self.incoming)
    
    def add(self) -> None:
        self.command.redirect = self.incoming


class Command:
    def __init__(self):
        self.positionals: dict[int, Positional] = {}
        self.flags: dict[str, Flag] = {}
        self.options: dict[str, Option] = {}
        self.redirect: Optional[Redirect] = None
        self.pos_manager: PositionManager = PositionManager() 

    def update(self, incoming: CommandComponent):
        updater = self.select_updater(incoming)
        updater.update(self, self.pos_manager, incoming)

    def select_updater(self, incoming: CommandComponent) -> Updater:
        match incoming:
            case Positional():
                return PositionalUpdater()
            case Flag():
                return FlagUpdater()
            case Option():
                return OptionUpdater()
            case Redirect():
                return RedirectUpdater()
            case _:
                raise RuntimeError(f'must pass CommandComponent to Command.update(). received {type(incoming)}')

    def get_inputs(self) -> list[CommandComponent]:
        components: list[CommandComponent] = []
        components += self.get_positionals()
        components += self.get_flags()
        components += self.get_options()
        return components
    
    def get_outputs(self) -> list[CommandComponent]:
        components: list[CommandComponent] = []
        for comp in self.get_inputs():
            if comp.gxvar and isinstance(comp.gxvar, OutputParam):
                components.append(comp)
        if self.redirect:
            components.append(self.redirect)
        return components

    def get_linked_gxparams(self) -> list[Param]:
        components: list[CommandComponent] = []
        components += self.get_inputs()
        components += self.get_outputs()
        gxparams = [c.gxvar for c in components]
        return [p for p in gxparams if p is not None]

    def get_positionals(self) -> list[Positional]:
        return list(self.positionals.values())

    def get_positional(self, cmd_pos: int) -> Optional[Positional]:
        if cmd_pos in self.positionals:
            return self.positionals[cmd_pos]
        return None

    def get_flags(self) -> list[Flag]:
        return list(self.flags.values())

    def get_flag(self, query_prefix: str) -> Optional[Flag]:
        if query_prefix in self.flags:
            return self.flags[query_prefix]
        return None

    def get_options(self) -> list[Option]:
        return list(self.options.values())

    def get_option(self, query_prefix: str) -> Optional[Option]:
        if query_prefix in self.options:
            return self.options[query_prefix]
        return None

    def get_input_positions(self) -> list[Tuple[int, CommandComponent]]:
        inputs = self.get_inputs()
        return format_input_positions(inputs)

    def get_base_command(self) -> list[str]:
        input_positions = self.get_input_positions()
        base_components = [inp for pos, inp in input_positions if pos == 0]
        base_cmd = [c.get_default_value() for c in base_components]
        return base_cmd

    # string representations
    def __str__(self) -> str:
        return f""" \
##### Command #####

positionals: ------------
{'main value':20}{'optional':>10}
{self._get_components_list_as_str('positional')}

flags: ------------
{'prefix':20}{'optional':>10}
{self._get_components_list_as_str('flag')}

options: ------------
{'prefix':30}{'main value':20}{'optional':>10}
{self._get_components_list_as_str('option')}"""

    def _get_components_list_as_str(self, ctype: str='positional') -> str:
        funcmap: dict[str, Callable[[], list[CommandComponent]]]  = {
            'positional': self.get_positionals,
            'flag': self.get_flags,
            'option': self.get_options,
        }
        outstr: str = ''
        for comp in funcmap[ctype]():
            outstr += comp.__str__() + '\n'
        return outstr
    