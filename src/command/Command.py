

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Optional, Callable
from command.cmdstr.CommandString import CommandString

from command.components.inputs import Positional, Flag, Option
from command.components.outputs import RedirectOutput
from command.components.CommandComponent import CommandComponent



class Updater(ABC):
    command: Command
    incoming: Positional | Flag | Option | RedirectOutput
    
    @abstractmethod
    def update(self, command: Command, incoming: Any) -> None:
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

    def update(self, command: Command, incoming: Positional) -> None:
        self.command = command
        self.incoming = incoming
        if self.should_merge():
            self.merge()
        else:
            self.add()

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

    def update(self, command: Command, incoming: Flag) -> None:
        self.command = command
        self.incoming = incoming
        if self.should_merge():
            self.merge()
        else:
            self.add()

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

    def update(self, command: Command, incoming: Option) -> None:
        self.command = command
        self.incoming = incoming
        if self.should_merge():
            self.merge()
        else:
            self.add()

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


class RedirectOutputUpdater(Updater):
    command: Command
    incoming: RedirectOutput

    def update(self, command: Command, incoming: RedirectOutput) -> None:
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
    def __init__(self, xmlcmdstr: CommandString):
        self.xmlcmdstr: CommandString = xmlcmdstr
        self.positionals: dict[int, Positional] = {}
        self.flags: dict[str, Flag] = {}
        self.options: dict[str, Option] = {}
        self.redirect: Optional[RedirectOutput] = None

    def update(self, incoming: CommandComponent) -> None:
        updater = self.select_updater(incoming)
        updater.update(self, incoming)

    def select_updater(self, incoming: CommandComponent) -> Updater:
        match incoming:
            case Positional():
                return PositionalUpdater()
            case Flag():
                return FlagUpdater()
            case Option():
                return OptionUpdater()
            case RedirectOutput():
                return RedirectOutputUpdater()
            case _:
                raise RuntimeError(f'must pass CommandComponent to Command.update(). received {type(incoming)}')

    def set_cmd_positions(self) -> None:
        options_pos: int = self.get_options_position()
        for flag in self.get_flags():
            flag.cmd_pos = options_pos
        for option in self.get_options():
            option.cmd_pos = options_pos
        
        pos_ptr: int = 1
        for positional in self.get_non_base_positionals():
            if pos_ptr == options_pos:
                pos_ptr += 1
            positional.cmd_pos = pos_ptr
            pos_ptr += 1

    def get_options_position(self) -> int:
        """
        returns cmd_pos for options and flags. 
        base command will always occupy cmd_pos == 0
        """
        i: int = 0
        positionals = self.get_non_base_positionals()
        while i < len(positionals) and positionals[i].before_opts:
            i += 1
        return i + 1

    def list_all_inputs(self) -> list[CommandComponent]:
        components: list[CommandComponent] = []
        components += self.get_positionals()
        components += self.get_flags()
        components += self.get_options()
        return components

    def get_inputs(self) -> list[CommandComponent]:
        components: list[CommandComponent] = []
        components += self.get_non_base_positionals()
        components += self.get_flags()
        components += self.get_options()
        return components

    def get_outputs(self) -> list[CommandComponent]:
        # just returns redirect component if present.
        # other outputs are handled by ToolFactory
        components: list[CommandComponent] = []
        if self.redirect:
            components.append(self.redirect)
        return components

    def get_base_positionals(self) -> list[Positional]:
        positionals = self.get_positionals()
        positionals = [p for p in positionals if p.before_opts]
        positionals = [p for p in positionals if not p.gxparam]
        positionals = [p for p in positionals if p.has_single_value()]
        return positionals

    def get_non_base_positionals(self) -> list[Positional]:
        base_positionals = self.get_base_positionals()
        all_positionals = self.get_positionals()
        return [p for p in all_positionals if p not in base_positionals]

    def get_positionals(self) -> list[Positional]:
        """returns positionals in sorted order"""
        positions_components = list(self.positionals.items())
        positions_components.sort(key=lambda x: x[0])
        return [p[1] for p in positions_components]

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
    