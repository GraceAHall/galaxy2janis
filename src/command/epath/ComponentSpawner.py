


from abc import ABC, abstractmethod

from command.components.CommandComponent import CommandComponent
from command.components.Flag import Flag
from command.components.Option import Option
from command.components.Positional import Positional
from command.tokens.Tokens import Token


class ComponentSpawner(ABC):
    @abstractmethod
    def spawn(self, ctoken: Token, ntokens: list[Token], epath_id: int, delim: str=' ') -> CommandComponent:
        """creates a specific CommandComponent"""
        ...

class FlagComponentSpawner(ComponentSpawner):
    def spawn(self, ctoken: Token, ntokens: list[Token], epath_id: int, delim: str=' ') -> Flag:
        return Flag(prefix=ctoken.text)

    def spawn_from_opt(self, option: Option) -> Flag:
        flag = Flag(prefix=option.prefix)
        gxvar = option.gxvar if option.gxvar_attachment == 1 else None
        flag.gxvar = gxvar
        return flag

class OptionComponentSpawner(ComponentSpawner):
    def spawn(self, ctoken: Token, ntokens: list[Token], epath_id: int, delim: str=' ') -> Option:
        return Option(
            prefix=ctoken.text,
            values=[ntoken.text for ntoken in ntokens],
            epath_id=epath_id,
            delim=delim
        )

class PositionalComponentSpawner(ComponentSpawner):
    def spawn(self, ctoken: Token, ntokens: list[Token], epath_id: int, delim: str=' ') -> Positional:
        return Positional(value=ctoken.text, epath_id=epath_id)
        


spawners = {
    'option': OptionComponentSpawner(),
    'flag': FlagComponentSpawner(),
    'positional': PositionalComponentSpawner()
}

def spawn_component(comp_type: str, ctoken: Token, ntokens: list[Token], epath_id: int, delim: str=' ') -> CommandComponent:
    spawner = spawners[comp_type]
    return spawner.spawn(ctoken, ntokens, epath_id, delim=delim)

