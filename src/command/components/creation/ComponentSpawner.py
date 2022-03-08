


from abc import ABC, abstractmethod

from command.cmdstr.CommandWord import CommandWord
from command.components.CommandComponent import CommandComponent
from command.components.Flag import Flag
from command.components.Option import Option
from command.components.Positional import Positional
import command.epath.utils as component_utils



class ComponentSpawner(ABC):
    @abstractmethod
    def create(self, cword: CommandWord, nwords: list[CommandWord]) -> CommandComponent:
        """creates a specific CommandComponent"""
        ...

class FlagComponentSpawner(ComponentSpawner):
    def create(self, cword: CommandWord, nwords: list[CommandWord]) -> Flag:
        return Flag(prefix=cword.token.text)

    def create_from_opt(self, option: Option) -> Flag:
        flag = Flag(prefix=option.prefix)
        gxvar = option.gxvar if option.gxvar_attachment == 1 else None
        flag.gxvar = gxvar
        return flag

class OptionComponentSpawner(ComponentSpawner):
    def create(self, cword: CommandWord, nwords: list[CommandWord]) -> Option:
        return Option(
            prefix=cword.token.text,
            value=[nword.token.text for nword in nwords],
            delim=cword.nextword_delim
        )

class PositionalComponentSpawner(ComponentSpawner):
    def create(self, cword: CommandWord, nwords: list[CommandWord]) -> Positional:
        return Positional(value=cword.token.text)
        

def init_spawner(cword: CommandWord, nwords: list[CommandWord]) -> ComponentSpawner:
    if component_utils.is_flag(cword.token, nword.token):
        return FlagComponentSpawner(cword.token, nword.token)
    elif component_utils.is_option(cword.token, nword.token):
        return OptionComponentSpawner(cword.token, nword.token)
    # positional - this has to happen last, as last resort. just trust me.
    else:
        return PositionalComponentSpawner(cword.token, nword.token)



