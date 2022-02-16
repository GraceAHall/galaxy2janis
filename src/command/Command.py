


from typing import Optional

from command.components.Positional import Positional
from command.components.Flag import Flag
from command.components.Option import Option
from command.components.linux_constructs import Redirect


class Command:
    def __init__(self):
        self.positionals: dict[int, Positional] = {}
        self.flags: dict[str, Flag] = {}
        self.options: dict[str, Option] = {}
        self.redirect: Optional[Redirect] = None

    def update_positionals(self, incoming: Positional) -> None:
        pass
    
    def update_flags(self, incoming: Flag) -> None:
        pass
    
    def update_redirect(self, incoming: Redirect) -> None:
        if self.redirect:
            raise RuntimeError(f'command already has redirect')
        self.redirect = incoming

    def update_components_presence_array(self) -> None:
        for component in list(self.flags.values()) + list(self.options.values()):
            component.update_presence_array(self.ingested_cmdstr_index)

    





    # def parse_positionals(self, command_string: CommandString) -> None:
    #     """
    #     providing a list of tokens allows the command to be updated with new info.
    #     the list of tokens could be from initial tool xml parsing, or from
    #     templated command line strings passed through galaxy tool evaluation engine.
    #     """
    #     # iterate through command words (with next word for context)
    #     i = 0
    #     command_block = command_string.best_block

    #     while i < len(command_block.tokens) - 1:
    #         self.step_size = 2
    #         curr_tokens = command_block.tokens[i]
    #         next_tokens = command_block.tokens[i+1]

    #         for ctoken in curr_tokens:  
    #             if ctoken.type == TokenType.KV_PAIR: 
    #                 self.opts_encountered = True
    #                 self.step_size = 1
    #                 continue  # this is implied, but looks clearer this way
                
    #             else:
    #                 for ntoken in next_tokens:
    #                     if not self.is_stdout(ctoken, ntoken):
    #                         component = self.make_component(ctoken, ntoken)
    #                         self.update_components(component, disallow=[Flag, Option])

    #         i += self.step_size


    

    # def update_components(self, the_comp: CommandComponent, disallow: list[CommandComponent]=[]) -> None:
    #     """
    #     TODO XML parsing

    #     attempts to update tool knowledge using a CommandComponent.
    #     the component (positional, flag, option) may already be registered in the Command.
        
    #     if no component exists, add the component. 
    #     if it looks the same as another known component, update that comp's sources 
    #     (want to keep a reference of all the occurances of that component).
    #     if it changes our understanding of the command string (ie what we thought was
    #     an option actually looks like a flag in this context), redefine that component 
    #     to be the correct form. 
    #     """        
    #     # improve component identification using prev known components
    #     cached_comp = self.get_component(the_comp)
    #     the_comp = self.refine_component_using_reference(the_comp, cached_comp)
        
    #     # update step size for token iteration
    #     if isinstance(the_comp, Positional) or isinstance(the_comp, Flag):
    #         self.step_size = 1

    #     if not isinstance(the_comp, Positional):
    #         self.opts_encountered = True
        
    #     # update 
    #     # TODO fix this is bad
    #     if type(the_comp) not in disallow:
    #         if isinstance(the_comp, Positional):
    #             self.update_positionals(the_comp)
            
    #         elif isinstance(the_comp, Flag):
    #             if isinstance(cached_comp, Option):
    #                 the_comp = self.reassign_option_as_flag(cached_comp, the_comp)
    #             else:
    #                 self.update_flags(the_comp)
                
    #         elif isinstance(the_comp, Option):
    #             self.update_options(the_comp)  
    

    # def get_component(self, query_comp: CommandComponent) -> Optional[CommandComponent]:
    #     if isinstance(query_comp, Positional):
    #         pos = query_comp.pos
    #         if pos in self.positionals:
    #             return self.positionals[pos]

    #     else:
    #         for key, comp in list(self.options.items()) + list(self.flags.items()):
    #             if key == query_comp.prefix:
    #                 return comp

    #     return None


    # def get_components_possessing_gxobj(self, 
    #         query_name: str, 
    #         valid_types: list[Union[CommandComponent, Output]] = None
    #     ) -> Union[CommandComponent, Output]:
    #     """
    #     function signature looks a little whack but better than a long line
    #     gets any component which has the provided gxobj attached.
    #     can restrict to specific type using restrict_type
    #     """
    #     all_components = self.get_all_components()
    #     valid_components = [c for c in all_components if c.galaxy_object.name == query_name]
    #     if valid_types:
    #         valid_components = [c for c in valid_components if type(c) in valid_types]
    #     return valid_components


    # def refine_component_using_reference(self, incoming: CommandComponent, ref_comp: Optional[CommandComponent]) -> CommandComponent:
    #     """
    #     allows us to change guess of the command component using cached components
        
    #     example: 
    #     if the incoming component is an option, this could also potentially be a flag + positional. if the ref_comp found was a flag, we know this 'option' is actually a flag followed by a positional

    #     """
    #     # nothing to compare against
    #     if ref_comp is None:
    #         return incoming
        
    #     # if we're parsing the tool xml command section
    #     # always want to favour the components extracted while 
    #     # parsing tool tests and workflow steps. 
    #     # tool xml format less reliable than valid command strings
    #     if self.cmd_source == 'xml':
    #         return self.cast_component(incoming, ref_comp)
    #     else:
    #         # overrule component as Flag
    #         if isinstance(incoming, Option) and isinstance(ref_comp, Flag):
    #             token = incoming.sources[0]
    #             return self.make_flag(token)

    #     # more robust stuff here? 
    #     # checking arguments of options for positional overruling? 
    #     return incoming
        

    # def cast_component(self, query: CommandComponent, ref: CommandComponent) -> CommandComponent:
    #     """
    #     casts query component to be same type as ref. 
    #     returns new CommandComponent instance to do this. 
    #     """
        
    #     # nothing to cast
    #     if type(query) == type(ref):
    #         return query
        
    #     # can't cast this
    #     elif isinstance(query, Positional):
    #         return query
        
    #     # flag to option
    #     elif isinstance(query, Flag) and isinstance(ref, Option):
    #         return Option(query.prefix)
        
    #     # option to flag
    #     elif isinstance(query, Option) and isinstance(ref, Flag):
    #         return Option(query.prefix)


    # def update_positionals_old(self, incoming: Positional) -> None:
    #     pos = incoming.pos
    #     if pos not in self.positionals:
    #         self.positionals[pos] = incoming
    #     else:
    #         self.positionals[pos].merge(incoming)

    #     self.positional_count += 1


    # def reassign_option_as_flag(self, the_opt: Option, the_flag: Flag) -> Flag:
    #     key = the_opt.prefix
    #     del self.options[key]
    #     return the_flag


    # def update_flags_old(self, incoming: Flag) -> None:
    #     key = incoming.prefix
    #     if key not in self.flags:
    #         self.flags[key] = incoming
    #     else:
    #         self.flags[key].merge(incoming)
        
    #     self.flags[key].set_presence(True)


    # def update_options(self, incoming: Option) -> None:
    #     key = incoming.prefix
    #     if key not in self.options:
    #         self.options[key] = incoming
    #     else:
    #         self.options[key].merge(incoming)
        
    #     self.options[key].set_presence(True)


    


    

    
    # def get_all_components(self) -> list[Union[CommandComponent, Output]]:
    #     out = []
    #     out += self.get_positionals()
    #     out += self.get_flags()
    #     out += self.get_options()
    #     out += self.get_outputs()
    #     return out
      

    # def get_positionals(self) -> list[Positional]:
    #     """
    #     returns list of positionals in order
    #     """
    #     positionals = list(self.positionals.values())
    #     positionals.sort(key = lambda x: x.pos)
    #     return positionals

    
    # def remove_positional(self, query_pos: int) -> None:
    #     """
    #     removes positional and renumbers remaining positionals, flags and options
    #     """
    #     if query_pos in self.positionals:
    #         del self.positionals[query_pos]

    #     self.shift_input_positions(startpos=query_pos, amount=-1)


    # def get_flags(self) -> list[Flag]:
    #     """
    #     returns list of flags in alphabetical order
    #     """
    #     flags = list(self.flags.values())
    #     flags.sort(key=lambda x: x.prefix)
    #     return flags


    # def get_options(self) -> list[Option]:
    #     """
    #     returns list of positionals in order
    #     """
    #     options = list(self.options.values())
    #     options.sort(key=lambda x: x.prefix.lstrip('-'))
    #     return options

    
    # def get_outputs(self) -> list[Output]:
    #     """
    #     returns list of outputs in order
    #     """
    #     outputs = self.outputs
    #     outputs.sort(key=lambda x: x.galaxy_object.name)
    #     return outputs


    # def set_component_positions(self) -> None:
    #     options_start = self.get_options_position()

    #     # update positionals
    #     self.shift_input_positions(startpos=options_start, amount=1)
        
    #     # update flags and opts position
    #     self.set_flags_options_position(options_start) 

        
    # def get_options_position(self) -> int:
    #     # positionals will be sorted list in order of position
    #     # can loop through and find the first which is 
    #     # 'is_after_options' and store that int
    #     positionals = self.get_positionals()

    #     options_start = len(positionals)
    #     for positional in positionals:
    #         if positional.is_after_options:
    #             options_start = positional.pos
    #             break
        
    #     return options_start
   

    # def shift_input_positions(self, startpos: int = 0, amount: int = 1) -> None:
    #     """
    #     shifts positionals position [amount] 
    #     starting at [startpos]
    #     ie if we have   inputs at 0,1,4,5,
    #                     shift_input_positions(2, -2)
    #                     inputs now at 0,1,2,3
    #     """
    #     for input_category in [self.positionals, self.flags, self.options]:
    #         for the_input in input_category.values():
    #             if the_input.pos >= startpos:
    #                 the_input.pos = the_input.pos + amount 

  
    # def set_flags_options_position(self, new_position: int) -> None:
    #     for input_category in [self.flags, self.options]:
    #         for the_input in input_category.values():
    #             the_input.pos = new_position


    # def __str__(self) -> str:
    #     out_str = ''
    #     out_str += '\npositionals ---------\n'
    #     out_str += f'{"pos":<10}{"values":40}{"gx_ref":20}{"after opts":>5}\n'
    #     for p in self.positionals.values():
    #         out_str += p.__str__() + '\n'

    #     out_str += '\nflags ---------------\n'
    #     out_str += f'{"pos":<10}{"prefix":20}{"values":40}{"gx_ref":20}\n'
    #     for f in self.flags.values():
    #         out_str += f.__str__() + '\n'

    #     out_str += '\noptions -------------\n'
    #     out_str += f'{"pos":<10}{"prefix":20}{"values":40}{"gx_ref":20}\n'
    #     for opt in self.options.values():
    #         out_str += opt.__str__() + '\n'
        
    #     return out_str

