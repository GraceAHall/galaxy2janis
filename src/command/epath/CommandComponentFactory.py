



# from abc import ABC, abstractmethod

# # from command.cmdstr.CommandWord import CommandWord
# # from command.cmdstr.CommandWordifier import CommandWordifier
# from command.components.CommandComponent import CommandComponent
# from command.components.inputs import Positional, Flag, Option
# from command.components.inputs.InputComponentFactory import init_spawner



# ## strategies to produce components given current word and next word        
# class ComponentCreationStrategy(ABC):
#     cword: CommandWord
#     nword: CommandWord
    
#     @abstractmethod
#     def create(self) -> list[CommandComponent]:
#         """creates list of command components using cword and nword"""
#         ...
        

# class SingleComponentCreationStrategy(ComponentCreationStrategy):
#     def __init__(self, cword: CommandWord, nword: CommandWord):
#         self.cword = cword
#         self.nword = nword
    
#     def create(self) -> list[CommandComponent]:
#         """creates list of command components using cword and nword"""
#         new_component = self.make_component()
#         new_component = self.transfer_gxparams(new_component)
#         return [new_component]

#     def make_component(self) -> CommandComponent:
#         spawner = init_spawner(self.cword, self.nword)
#         return spawner.create(self.cword, self.nword)
    
    
    
#     def transfer_gxparams(self, component: CommandComponent) -> CommandComponent:
#         match component:
#             case Flag():
#                 component.gxparam = self.cword.gxparam
#             case Option():
#                 if self.cword.gxparam:
#                     component.gxparam = self.cword.gxparam
#                 elif self.nword.gxparam:
#                     component.gxparam = self.nword.gxparam
#             case Positional():
#                 component.gxparam = self.cword.gxparam
#             case _:
#                 pass
#         return component


# class MultipleComponentCreationStrategy(ComponentCreationStrategy):
#     def __init__(self, cword: CommandWord, nword: CommandWord, wordifier: CommandWordifier):
#         self.cword = cword
#         self.nword = nword
#         self.wordifier = wordifier
    
#     def create(self) -> list[CommandComponent]:
#         """creates list of command components using cword and nword"""
#         """
#         iterates through possible execution paths 
#         ie --db $adv.db
#         where $adv.db is a select param with values 
#         [resfiner, card, par]
#         would produce 3 possible execution paths: 
#         --db resfinder, --db card, --db par
#         presents these as a list of commandwords which we iterate through,
#         converting the commandwords into components
#         """
#         components: list[CommandComponent] = []
#         #efork = ExecutionPath(self.cword, self.nword, self.wordifier)
#         for path in efork.forks():
#             path_components = self.iter_words(path)
#             path_components = self.transfer_gxparams(path_components)
#             components += path_components
#         return components

#     def iter_words(self, cmdwords: list[CommandWord]) -> list[CommandComponent]:
#         out: list[CommandComponent] = []
#         i = 0
#         while i < len(cmdwords) - 2:
#             step_size = 1
#             cword = cmdwords[i]
#             nword = cmdwords[i + 1]
#             single_creator = SingleComponentCreationStrategy(cword, nword)
#             components = single_creator.create()
#             assert(len(components) == 1)
#             out += components
#             if isinstance(components[0], Option):
#                 step_size = 2
#             i += step_size
#         return out
    
#     def transfer_gxparams(self, components: list[CommandComponent]) -> list[CommandComponent]:
#         """
#         because the second cmdword (nword) value is truncated to a single word,
#         we know that the only way a gxparam could originate from the nword value is 
#         if the last component is an option.
#         example: 
#         cword = --db, nword = $adv.db
#         cword gets expanded to '--db', and $adv.db expands to ['card', 'resfinder']
#         then the executionpaths are:
#         --db card,   --db resfinder
#         in these situations, the card and resfinder came from nword's gxparam ($adv.db)
#         all other situations, just move the gxparam from cword to the component. 
#         """
#         # can attempt to transfer cword's gxparam to 
#         for component in components:
#             component.gxparam = self.cword.gxparam
        
#         # last component
#         if isinstance(components[-1], Option):
#             if not components[-1].gxparam:
#                 components[-1].gxparam = self.nword.gxparam

#         return components
 


# ## main factory
# class CommandComponentFactory: 
#     cword: CommandWord
#     nword: CommandWord
#     """
#     the attrs above are set using the create() method. 
#     just to avoid passing around a lot
#     """
    
#     def __init__(self, xmltool: XMLToolDefinition):
#         self.wordifier = CommandWordifier(xmltool) # for annoying option/bool params (have many possible values)

#     def cast_to_flag(self, option: Option) -> Flag:
#         spawner = FlagComponentFactory()
#         return spawner.create_from_opt(option)

#     def create(self, cword: CommandWord, nword: CommandWord) -> list[CommandComponent]:
#         """
#         main entry point for creating commandcomponents
#         depending on the two cmdwords (cword, nword), the actual strategy for creating 
#         components is different. 
#         this function just selects which strategy to use, the delegates creating components to 
#         that strategy.
#         """
#         self.cword = cword
#         self.nword = nword
#         creation_strategy = self.get_creation_strategy()
#         return creation_strategy.create()

#     def get_creation_strategy(self) -> ComponentCreationStrategy:
#         # not galaxy options or bool param
#         if component_utils.word_is_bool_select(self.cword):
#             return MultipleComponentCreationStrategy(self.cword, self.nword, self.wordifier)
#         elif component_utils.word_is_bool_select(self.nword):
#             return MultipleComponentCreationStrategy(self.cword, self.nword, self.wordifier)
#         return SingleComponentCreationStrategy(self.cword, self.nword)

    
    
    
    



