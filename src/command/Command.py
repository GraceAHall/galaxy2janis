

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Optional

from command.components.Positional import Positional
from command.components.Flag import Flag
from command.components.Option import Option
from command.components.linux_constructs import Redirect

CommandComponent = Positional | Flag | Option



class Updater(ABC):

    @abstractmethod
    def update(self, command: Command, incoming: Any, cmdstr_index: int) -> None:
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
    cmdstr_index: int

    def update(self, command: Command, incoming: Positional, cmdstr_index: int) -> None:
        """updates the command's store of CommandComponents with the incoming component"""
        self.command = command
        self.incoming = incoming
        self.cmdstr_index = cmdstr_index
        if self.should_merge():
            self.merge()
        else:
            self.add()

    def should_merge(self) -> bool:
        cmd_pos = self.command.positional_ptr
        existing_comp = self.command.get_positional(cmd_pos)
        if existing_comp:
            return True
        return False
    
    def merge(self) -> None:
        cmd_pos = self.command.positional_ptr
        existing_comp = self.command.get_positional(cmd_pos)
        if existing_comp:
            existing_comp.update(self.incoming, self.cmdstr_index)
    
    def add(self) -> None:
        cmd_pos = self.command.positional_ptr
        self.command.positionals[cmd_pos] = self.incoming
        self.command.positional_ptr += 1


class FlagUpdater(Updater):
    command: Command
    incoming: Flag
    cmdstr_index: int

    def update(self, command: Command, incoming: Flag, cmdstr_index: int) -> None:
        """updates the command's store of CommandComponents with the incoming component"""
        self.command = command
        self.incoming = incoming
        self.cmdstr_index = cmdstr_index
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
    cmdstr_index: int

    def update(self, command: Command, incoming: Option, cmdstr_index: int) -> None:
        """updates the command's store of CommandComponents with the incoming component"""
        self.command = command
        self.incoming = incoming
        self.cmdstr_index = cmdstr_index
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
            existing_comp.update(self.incoming, self.cmdstr_index)
    
    def add(self) -> None:
        prefix = self.incoming.prefix
        self.command.options[prefix] = self.incoming


class Command:
    def __init__(self):
        self.positional_ptr: int = 0
        self.positionals: dict[int, Positional] = {}
        self.flags: dict[str, Flag] = {}
        self.options: dict[str, Option] = {}
        self.redirect: Optional[Redirect] = None

    def update(self, incoming: CommandComponent, cmdstr_index: int):
        updater = self.select_updater(incoming)
        updater.update(self, incoming, cmdstr_index)

    def select_updater(self, incoming: CommandComponent) -> Updater:
        match incoming:
            case Positional():
                return PositionalUpdater()
            case Flag():
                return FlagUpdater()
            case Option():
                return OptionUpdater()
            case _:
                raise RuntimeError(f'must pass CommandComponent to Command.update(). received {type(incoming)}')

    def get_all_components(self) -> list[CommandComponent]:
        components: list[CommandComponent] = []
        components += self.get_positionals()
        components += self.get_flags()
        components += self.get_options()
        return components

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
 

