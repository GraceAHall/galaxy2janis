


from abc import ABC, abstractmethod

from ..CommandComponent import CommandComponent
from .Flag import Flag
from .Option import Option
from .Positional import Positional


class InputComponentFactory(ABC):
    @abstractmethod
    def spawn_cmdstr(self, ctext: str, ntexts: list[str], delim: str=' ') -> CommandComponent:
        """creates a specific CommandComponent"""
        ...

class FlagComponentFactory(InputComponentFactory):
    def spawn_cmdstr(self, ctext: str, ntexts: list[str], delim: str=' ') -> Flag:
        return Flag(prefix=ctext)

    def spawn_from_opt(self, option: Option) -> Flag:
        flag = Flag(prefix=option.prefix)
        gxparam = option.gxparam if option.gxparam_attachment == 1 else None
        flag.gxparam = gxparam
        return flag

class OptionComponentFactory(InputComponentFactory):
    def spawn_cmdstr(self, ctext: str, ntexts: list[str], delim: str=' ') -> Option:
        return Option(
            prefix=ctext,
            values=ntexts,
            delim=delim
        )

class PositionalComponentFactory(InputComponentFactory):
    def spawn_cmdstr(self, ctext: str, ntexts: list[str], delim: str=' ') -> Positional:
        return Positional(value=ctext)


        


spawners = {
    'option': OptionComponentFactory(),
    'flag': FlagComponentFactory(),
    'positional': PositionalComponentFactory()
}

def spawn_component(comp_type: str, ctext: str, ntexts: list[str], delim: str=' ') -> CommandComponent:
    spawner = spawners[comp_type]
    return spawner.spawn_cmdstr(ctext, ntexts, delim=delim)


# def spawn_component_from_gxparam(comp_type: str, ctext: str, ntexts: list[str], delim: str=' ') -> CommandComponent:
#     spawner = spawners[comp_type]
#     return spawner.spawn_gxparam(ctext, ntexts, delim=delim)

