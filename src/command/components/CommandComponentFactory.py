



from abc import ABC, abstractmethod
from copy import deepcopy

from command.cmdstr.CommandWord import CommandWord
from command.cmdstr.CommandWordifier import CommandWordifier

from command.tokens.Tokens import Token
from command.components.Flag import Flag
from command.components.Option import Option
from command.components.Positional import Positional
from command.components.ExecutionFork import ExecutionFork
import command.components.utils as component_utils

from tool.tool_definition import GalaxyToolDefinition

CommandComponent = Flag | Option | Positional


class ComponentSpawner(ABC):
    @abstractmethod
    def create(self, ctoken: Token, ntoken: Token, cmdstr_index: int) -> CommandComponent:
        """creates a specific CommandComponent"""
        ...

class FlagComponentSpawner(ComponentSpawner):
    def create(self, ctoken: Token, ntoken: Token, cmdstr_index: int) -> Flag:
        return Flag(
            prefix=ctoken.text,
            cmdstr_index=cmdstr_index
        )

    def create_from_opt(self, option: Option) -> Flag:
        gxvar = option.gxvar if option.gxvar_attachment == 1 else None
        return Flag(
            prefix=option.prefix,
            cmdstr_index=len(option.presence_array), # workaround
            gxvar=gxvar
        )

class OptionComponentSpawner(ComponentSpawner):
    def create(self, ctoken: Token, ntoken: Token, cmdstr_index: int) -> Option:
        return Option(
            prefix=ctoken.text,
            value=ntoken.text,
            cmdstr_index=cmdstr_index,
            delim=' ' # TODO change this ive split '=' and ':' delims without noting! 
        )

class PositionalComponentSpawner(ComponentSpawner):
    def create(self, ctoken: Token, ntoken: Token, cmdstr_index: int) -> Positional:
        return Positional(
            value=ctoken.text,
            cmdstr_index=cmdstr_index
        )


class CommandComponentFactory: 
    cword: CommandWord
    nword: CommandWord
    cmdstr_index: int
    """
    these values above are set using the create() method. 
    just to avoid passing around a lot
    """
    
    def __init__(self, tool: GalaxyToolDefinition):
        self.wordifier = CommandWordifier(tool) # for annoying option/bool params (have many possible values)

    def cast_to_flag(self, option: Option) -> Flag:
        spawner = FlagComponentSpawner()
        return spawner.create_from_opt(option)

    def create(self, cword: CommandWord, nword: CommandWord, cmdstr_index: int) -> list[CommandComponent]:
        self.cmdstr_index = cmdstr_index
        self.cword = cword
        self.nword = nword
        if self.is_simple_case():
            return self.make_simple()
        return self.make_complex()

    def is_simple_case(self) -> bool:
        # not galaxy options or bool param
        if component_utils.word_is_bool_select(self.cword):
            return False
        elif component_utils.word_is_bool_select(self.nword):
            return False
        return True

    def make_simple(self) -> list[CommandComponent]:
        new_component = self.make_component(self.cword.token, self.nword.token, self.cmdstr_index)
        new_component = self.transfer_cmdword_attrs(new_component)
        return [new_component]

    def transfer_cmdword_attrs(self, component: CommandComponent) -> CommandComponent:
        match component:
            case Flag():
                component.gxvar = self.cword.gxvar
            case Option():
                if self.cword.gxvar:
                    component.gxvar = self.cword.gxvar
                elif self.nword.gxvar:
                    component.gxvar = self.nword.gxvar
            case Positional():
                component.gxvar = self.cword.gxvar
        return component

    def make_component(self, ctoken: Token, ntoken: Token, cmdstr_index: int) -> CommandComponent:
        spawner = self.select_spawner(ctoken, ntoken)
        return spawner.create(ctoken, ntoken, cmdstr_index)

    def select_spawner(self, ctoken: Token, ntoken: Token) -> ComponentSpawner:
        if component_utils.is_flag(ctoken, ntoken):
            return FlagComponentSpawner()
        elif component_utils.is_option(ctoken, ntoken):
            return OptionComponentSpawner()
        # positional - this has to happen last, as last resort. just trust me.
        else:
            return PositionalComponentSpawner()
    
    def make_complex(self) -> list[CommandComponent]:
        """
        iterates through possible execution paths 
        ie --db $adv.db
        where $adv.db is a select param with values 
        [resfiner, card, par]
        would produce 3 possible execution paths: 
        --db resfinder, --db card, --db par
        presents these as a list of commandwords which we iterate through,
        converting the commandwords into components
        """
        cword = deepcopy(self.cword)
        nword = deepcopy(self.nword)
        components: list[CommandComponent] = []
        efork = ExecutionFork(cword, nword, self.wordifier)
        for path in efork.forks():
            path_components = self.iter_words(path)
            path_components = self.transfer_gxvars_complex(cword, nword, path_components)
            components += path_components
        return components

    def iter_words(self, cmdwords: list[CommandWord]) -> list[CommandComponent]:
        out: list[CommandComponent] = []
        i = 0
        while i < len(cmdwords) - 2:
            step_size = 1
            cword = cmdwords[i]
            nword = cmdwords[i + 1]
            components = self.create(cword, nword, self.cmdstr_index)
            assert(len(components) == 1)
            out += components
            if isinstance(components[0], Option):
                step_size = 2
            i += step_size
        return out
    
    def transfer_gxvars_complex(self, cword: CommandWord, nword: CommandWord, components: list[CommandComponent]) -> list[CommandComponent]:
        """
        because the second cmdword (nword) value is truncated to a single word,
        we know that the only way a gxvar could originate from the nword value is 
        if the last component is an option.
        example: 
        cword = --db, nword = $adv.db
        cword gets expanded to '--db', and $adv.db expands to ['card', 'resfinder']
        then the executionpaths are:
        --db card,   --db resfinder
        in these situations, the card and resfinder came from nword's gxvar ($adv.db)
        all other situations, just move the gxvar from cword to the component. 
        """
        # can attempt to transfer cword's gxvar to 
        for component in components:
            component.gxvar = cword.gxvar
        
        # last component
        if isinstance(components[-1], Option):
            if not components[-1].gxvar:
                components[-1].gxvar = nword.gxvar

        return components
 



