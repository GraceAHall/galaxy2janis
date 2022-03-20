


from abc import ABC, abstractmethod

from command.components.CommandComponent import CommandComponent
from command.tokens.Tokens import Token
from .Flag import Flag
from .Option import Option
from .Positional import Positional


class InputComponentFactory(ABC):
    @abstractmethod
    def spawn(self, ctoken: Token, ntokens: list[Token], epath_id: int, delim: str=' ') -> CommandComponent:
        """creates a specific CommandComponent"""
        ...

class FlagComponentFactory(InputComponentFactory):
    def spawn(self, ctoken: Token, ntokens: list[Token], epath_id: int, delim: str=' ') -> Flag:
        return Flag(prefix=ctoken.text)

    def spawn_from_opt(self, option: Option) -> Flag:
        flag = Flag(prefix=option.prefix)
        gxparam = option.gxparam if option.gxparam_attachment == 1 else None
        flag.gxparam = gxparam
        return flag

class OptionComponentFactory(InputComponentFactory):
    def spawn(self, ctoken: Token, ntokens: list[Token], epath_id: int, delim: str=' ') -> Option:
        return Option(
            prefix=ctoken.text,
            values=[ntoken.text for ntoken in ntokens],
            epath_id=epath_id,
            delim=delim
        )

class PositionalComponentFactory(InputComponentFactory):
    def spawn(self, ctoken: Token, ntokens: list[Token], epath_id: int, delim: str=' ') -> Positional:
        return Positional(value=ctoken.text, epath_id=epath_id)
        


spawners = {
    'option': OptionComponentFactory(),
    'flag': FlagComponentFactory(),
    'positional': PositionalComponentFactory()
}

def spawn_input_component(comp_type: str, ctoken: Token, ntokens: list[Token], epath_id: int, delim: str=' ') -> CommandComponent:
    spawner = spawners[comp_type]
    return spawner.spawn(ctoken, ntokens, epath_id, delim=delim)

