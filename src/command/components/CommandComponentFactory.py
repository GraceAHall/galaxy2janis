



from abc import ABC, abstractmethod

from command.cmdstr.CommandWord import CommandWord
from command.cmdstr.CommandWordifier import CommandWordifier

from command.tokens.Tokens import Token
from command.components.Flag import Flag
from command.components.Option import Option
from command.components.Positional import Positional
from command.components.ExecutionFork import ExecutionFork
import command.components.utils as component_utils

from tool.tool_definition import GalaxyToolDefinition
from command.components.CommandComponent import CommandComponent


## strategies to initialise individual CommandComponents    
class ComponentSpawner(ABC):
    @abstractmethod
    def create(self, ctoken: Token, ntoken: Token) -> CommandComponent:
        """creates a specific CommandComponent"""
        ...

class FlagComponentSpawner(ComponentSpawner):
    def create(self, ctoken: Token, ntoken: Token) -> Flag:
        return Flag(prefix=ctoken.text)

    def create_from_opt(self, option: Option) -> Flag:
        flag = Flag(prefix=option.prefix)
        gxvar = option.gxvar if option.gxvar_attachment == 1 else None
        flag.gxvar = gxvar
        return flag

class OptionComponentSpawner(ComponentSpawner):
    def create(self, ctoken: Token, ntoken: Token) -> Option:
        return Option(
            prefix=ctoken.text,
            value=ntoken.text,
            delim=' ' # TODO change this ive split '=' and ':' delims without noting! 
        )

class PositionalComponentSpawner(ComponentSpawner):
    def create(self, ctoken: Token, ntoken: Token) -> Positional:
        return Positional(value=ctoken.text)



## strategies to produce components given current word and next word        
class ComponentCreationStrategy(ABC):
    cword: CommandWord
    nword: CommandWord
    
    @abstractmethod
    def create(self) -> list[CommandComponent]:
        """creates list of command components using cword and nword"""
        ...
        

class SingleComponentCreationStrategy(ComponentCreationStrategy):
    def __init__(self, cword: CommandWord, nword: CommandWord):
        self.cword = cword
        self.nword = nword
    
    def create(self) -> list[CommandComponent]:
        """creates list of command components using cword and nword"""
        new_component = self.make_component(self.cword.token, self.nword.token)
        new_component = self.transfer_gxvars(new_component)
        return [new_component]

    def make_component(self, ctoken: Token, ntoken: Token) -> CommandComponent:
        spawner = self.select_spawner(ctoken, ntoken)
        return spawner.create(ctoken, ntoken)
    
    def select_spawner(self, ctoken: Token, ntoken: Token) -> ComponentSpawner:
        if component_utils.is_flag(ctoken, ntoken):
            return FlagComponentSpawner()
        elif component_utils.is_option(ctoken, ntoken):
            return OptionComponentSpawner()
        # positional - this has to happen last, as last resort. just trust me.
        else:
            return PositionalComponentSpawner()
    
    def transfer_gxvars(self, component: CommandComponent) -> CommandComponent:
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
            case _:
                pass
        return component



class MultipleComponentCreationStrategy(ComponentCreationStrategy):
    def __init__(self, cword: CommandWord, nword: CommandWord, wordifier: CommandWordifier):
        self.cword = cword
        self.nword = nword
        self.wordifier = wordifier
    
    def create(self) -> list[CommandComponent]:
        """creates list of command components using cword and nword"""
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
        components: list[CommandComponent] = []
        efork = ExecutionFork(self.cword, self.nword, self.wordifier)
        for path in efork.forks():
            path_components = self.iter_words(path)
            path_components = self.transfer_gxvars(path_components)
            components += path_components
        return components

    def iter_words(self, cmdwords: list[CommandWord]) -> list[CommandComponent]:
        out: list[CommandComponent] = []
        i = 0
        while i < len(cmdwords) - 2:
            step_size = 1
            cword = cmdwords[i]
            nword = cmdwords[i + 1]
            single_creator = SingleComponentCreationStrategy(cword, nword)
            components = single_creator.create()
            assert(len(components) == 1)
            out += components
            if isinstance(components[0], Option):
                step_size = 2
            i += step_size
        return out
    
    def transfer_gxvars(self, components: list[CommandComponent]) -> list[CommandComponent]:
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
            component.gxvar = self.cword.gxvar
        
        # last component
        if isinstance(components[-1], Option):
            if not components[-1].gxvar:
                components[-1].gxvar = self.nword.gxvar

        return components
 


## main factory
class CommandComponentFactory: 
    cword: CommandWord
    nword: CommandWord
    """
    the attrs above are set using the create() method. 
    just to avoid passing around a lot
    """
    
    def __init__(self, tool: GalaxyToolDefinition):
        self.wordifier = CommandWordifier(tool) # for annoying option/bool params (have many possible values)

    def cast_to_flag(self, option: Option) -> Flag:
        spawner = FlagComponentSpawner()
        return spawner.create_from_opt(option)

    def create(self, cword: CommandWord, nword: CommandWord) -> list[CommandComponent]:
        """
        main entry point for creating commandcomponents
        depending on the two cmdwords (cword, nword), the actual strategy for creating 
        components is different. 
        this function just selects which strategy to use, the delegates creating components to 
        that strategy.
        """
        self.cword = cword
        self.nword = nword
        creation_strategy = self.get_creation_strategy()
        return creation_strategy.create()

    def get_creation_strategy(self) -> ComponentCreationStrategy:
        # not galaxy options or bool param
        if component_utils.word_is_bool_select(self.cword):
            return MultipleComponentCreationStrategy(self.cword, self.nword, self.wordifier)
        elif component_utils.word_is_bool_select(self.nword):
            return MultipleComponentCreationStrategy(self.cword, self.nword, self.wordifier)
        return SingleComponentCreationStrategy(self.cword, self.nword)

    
    
    
    



