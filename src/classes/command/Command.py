

# pyright: basic 

from re import L
from typing import Union, Optional

from classes.command.CommandString import CommandString
from classes.outputs.OutputRegister import OutputRegister
from classes.params.ParamRegister import ParamRegister
from classes.command.CommandComponents import Positional, Flag, Option, Stdout
from classes.command.Tokens import Token, TokenType
from galaxy.tool_util.parser.output_objects import ToolOutput
from galaxy.tools.parameters.basic import ToolParameter
from utils.token_utils import split_keyval_to_best_tokens 

CommandComponent = Union[Positional, Flag, Option]


class Command:
    def __init__(self, param_register: ParamRegister, out_register: OutputRegister):
        self.param_register = param_register
        self.out_register = out_register

        self.positionals: dict[int, Positional] = {}
        self.flags: dict[str, Flag] = {}
        self.options: dict[str, Option] = {}
        self.stdout: Stdout = Stdout()
        self.base_command: list[str] = []

        # iteration attributes
        self.cmd_source: str = 'test'
        self.step_size: int = 2
        self.opts_encountered: bool = False
        self.positional_count: int = 0


    def update(self, command_string: CommandString, source: str='test') -> None:
        """
        providing a list of tokens allows the command to be updated with new info.
        the list of tokens could be from initial tool xml parsing, or from
        templated command line strings passed through galaxy tool evaluation engine.
        this function just delegates what strategy to use to update command knowledge.
        """
        print(command_string.best_block)
        
        # reset attributes
        self.cmd_source = source
        self.opts_encountered = False
        
        # update options
        self.parse_flags_options_stdout(command_string)
        
        # update positionals
        if self.cmd_source != 'xml':
            self.positional_count = 0
            self.parse_positionals(command_string)
    
    
    def parse_flags_options_stdout(self, command_string: CommandString) -> None:
        """
        providing a list of tokens allows the command to be updated with new info.
        the list of tokens could be from initial tool xml parsing, or from
        templated command line strings passed through galaxy tool evaluation engine.
        """

        # iterate through command words (with next word for context)
        i = 0
        command_block = command_string.best_block

        while i < len(command_block.tokens) - 1:
            self.step_size = 2
            curr_tokens = command_block.tokens[i]
            next_tokens = command_block.tokens[i+1]

            for ctoken in curr_tokens:  

                # kv pair handling. add as option with correct delim. 
                if ctoken.type == TokenType.KV_PAIR: 
                    ctoken, ntoken, delim = split_keyval_to_best_tokens(ctoken, self.param_register, self.out_register)
                    option = self.make_option(ctoken, ntoken, delim=delim, splittable=False)
                    self.update_components(option)
                    self.step_size = 1
                    continue

                # everything else
                for ntoken in next_tokens:
                    # stdout
                    if self.is_stdout(ctoken, ntoken):
                        self.update_stdout(ntoken)

                    # flag, option
                    else:
                        naive_component = self.make_component(ctoken, ntoken)
                        self.update_components(naive_component, disallow=[Positional])

            i += self.step_size


    def parse_positionals(self, command_string: CommandString) -> None:
        """
        providing a list of tokens allows the command to be updated with new info.
        the list of tokens could be from initial tool xml parsing, or from
        templated command line strings passed through galaxy tool evaluation engine.
        """
        # iterate through command words (with next word for context)
        i = 0
        command_block = command_string.best_block

        while i < len(command_block.tokens) - 1:
            self.step_size = 2
            curr_tokens = command_block.tokens[i]
            next_tokens = command_block.tokens[i+1]

            for ctoken in curr_tokens:  
                if ctoken.type == TokenType.KV_PAIR: 
                    self.opts_encountered = True
                    self.step_size = 1
                    continue  # this is implied, but looks clearer this way
                
                else:
                    for ntoken in next_tokens:
                        if not self.is_stdout(ctoken, ntoken):
                            component = self.make_component(ctoken, ntoken)
                            self.update_components(component, disallow=[Flag, Option])

            i += self.step_size


    def calc_step_size(self, ctokens: list[Token], ntokens: list[Token]) -> int:
        for ctoken in ctokens:
            for ntoken in ntokens:
                
                if self.is_stdout(ctoken, ntoken):
                    return 2
                elif ctoken.type == TokenType.KV_PAIR:
                    return 1

                component = self.make_component(ctoken, ntoken)
                if type(component) == Flag or type(component) == Positional:
                    return 1

        return 2


    def is_stdout(self, ctoken: Token, ntoken: Token) -> bool:
        """
        """
        if ctoken.type == TokenType.LINUX_OP:
            if ntoken.type in [TokenType.RAW_STRING, TokenType.GX_OUT]:
                return True
        return False   


    def update_stdout(self, token: Token) -> None:
        self.stdout.add_token(token)


    def make_component(self, ctoken: Token, ntoken: Token) -> CommandComponent:
        # flag
        if self.is_flag(ctoken, ntoken):
            return self.make_flag(ctoken)
        # option
        elif self.is_option(ctoken, ntoken):
            return self.make_option(ctoken, ntoken)
        # positional
        else:
            # this has to happen last, as last resort
            # some examples of options which don't start with '-' exist. 
            return self.make_positional(ctoken)


    def make_flag(self, token: Token) -> Flag:
        flag = Flag(token.text)
        flag.add_token(token) 
        if token.gx_ref != '':
            flag.galaxy_object = self.get_gx_object(token)
        return flag 


    def get_gx_object(self, token: Token) -> Optional[Union[ToolParameter, ToolOutput]]:
        varname, gx_object = self.param_register.get(token.gx_ref, allow_lca=True)
        if gx_object is None:
            varname, gx_object = self.out_register.get(token.gx_ref, allow_lca=True)

        return gx_object


    def make_option(self, ctoken: Token, ntoken: Token) -> Option:
        opt = Option(ctoken.text)
        opt.add_token(ntoken)
        if ntoken.gx_ref != '':
            opt.galaxy_object = self.get_gx_object(ntoken)
        return opt


    def make_positional(self, token: Token) -> Positional:
        pos = self.positional_count
        posit = Positional(pos)
        posit.add_token(token)
        if token.gx_ref != '':
            posit.galaxy_object = self.get_gx_object(token)
        return posit
     

    def update_components(self, the_comp: CommandComponent, disallow: list[CommandComponent]=[]) -> None:
        """
        TODO XML parsing

        attempts to update tool knowledge using a CommandComponent.
        the component (positional, flag, option) may already be registered in the Command.
        
        if no component exists, add the component. 
        if it looks the same as another known component, update that comp's sources 
        (want to keep a reference of all the occurances of that component).
        if it changes our understanding of the command string (ie what we thought was
        an option actually looks like a flag in this context), redefine that component 
        to be the correct form. 
        """        
        # improve component identification using prev known components
        cached_comp = self.get_component(the_comp)
        the_comp = self.refine_component_using_reference(the_comp, cached_comp)
        
        # update step size for token iteration
        if type(the_comp) in [Positional, Flag]:
            self.step_size = 1

        if type(the_comp) != Positional:
            self.opts_encountered = True
        
        # update 
        if type(the_comp) not in disallow:
            if type(the_comp) == Positional:
                self.update_positionals(the_comp)
            
            elif type(the_comp) == Flag:
                if type(cached_comp) == Option:
                    the_comp = self.reassign_option_as_flag(cached_comp, the_comp)
                else:
                    self.update_flags(the_comp)
                
            elif type(the_comp) == Option:
                self.update_options(the_comp)  
    

    def get_component(self, query_comp: CommandComponent) -> Optional[CommandComponent]:
        if type(query_comp) == Positional:
            pos = query_comp.pos
            if pos in self.positionals:
                return self.positionals[pos]

        else:
            for key, comp in list(self.options.items()) + list(self.flags.items()):
                if key == query_comp.prefix:
                    return comp

        return None


    def refine_component_using_reference(self, incoming: CommandComponent, ref_comp: Optional[CommandComponent]) -> CommandComponent:
        """
        allows us to change guess of the command component using cached components
        
        example: 
        if the incoming component is an option, this could also potentially be a flag + positional. if the ref_comp found was a flag, we know this 'option' is actually a flag followed by a positional

        """
        # nothing to compare against
        if ref_comp is None:
            return incoming
        
        # if we're parsing the tool xml command section
        # always want to favour the components extracted while 
        # parsing tool tests and workflow steps. 
        # tool xml format less reliable than valid command strings
        if self.cmd_source == 'xml':
            return self.cast_component(incoming, ref_comp)
        else:
            # overrule component as Flag
            if type(incoming) == Option and type(ref_comp) == Flag:
                token = incoming.sources[0]
                return self.make_flag(token)

        # more robust stuff here? 
        # checking arguments of options for positional overruling? 
        return incoming
        

    def cast_component(self, query: CommandComponent, ref: CommandComponent) -> CommandComponent:
        """
        casts query component to be same type as ref. 
        returns new CommandComponent instance to do this. 
        """
        
        # nothing to cast
        if type(query) == type(ref):
            return query
        
        # can't cast this
        elif type(query) == Positional:
            return query
        
        # flag to option
        elif type(query) == Flag and type(ref) == Option:
            return Option(query.prefix)
        
        # option to flag
        elif type(query) == Option and type(ref) == Flag:
            return Flag(query.prefix)


    def update_positionals(self, incoming: Positional) -> None:
        pos = incoming.pos
        if pos not in self.positionals:
            self.positionals[pos] = incoming
        else:
            self.positionals[pos].merge(incoming)

        self.positional_count += 1


    def reassign_option_as_flag(self, the_opt: Option, the_flag: Flag) -> Flag:
        key = the_opt.prefix
        del self.options[key]
        return the_flag


    def update_flags(self, incoming: Flag) -> None:
        key = incoming.prefix
        if key not in self.flags:
            self.flags[key] = incoming
        else:
            self.flags[key].merge(incoming)


    def update_options(self, incoming: Option) -> None:
        key = incoming.prefix
        if key not in self.options:
            self.options[key] = incoming
        else:
            self.options[key].merge(incoming)


    def is_flag(self, ctoken: Token, ntoken: Token) -> bool:
        # is this a raw flag or option?
        curr_is_raw_flag = ctoken.type == TokenType.RAW_STRING and ctoken.text.startswith('-')

        # the current token has to be a flag 
        if curr_is_raw_flag:

            # next token is a flag
            next_is_raw_flag = ntoken.type == TokenType.RAW_STRING and ntoken.text.startswith('-')
            if next_is_raw_flag:
                return True

            # next token is linux operation
            elif ntoken.type == TokenType.LINUX_OP:
                return True
            
            # next token is key-val pair
            elif ntoken.type == TokenType.KV_PAIR:
                return True
            
            # this is the last command token
            elif ntoken.type == TokenType.END_COMMAND:
                return True
                
        return False


    def is_option(self, ctoken: Token, ntoken: Token) -> bool:
        # happens 2nd after 'is_flag()'
        # already know that its not a flag, so if the current token
        # looks like a flag/option, it has to be an option. 

        curr_is_raw_flag = ctoken.type == TokenType.RAW_STRING and ctoken.text.startswith('-')

        # the current token has to be a flag 
        if curr_is_raw_flag:
            return True
                
        return False
      

    def get_positionals(self) -> list[Positional]:
        """
        returns list of positionals in order
        """
        positionals = list(self.positionals.values())
        positionals.sort(key = lambda x: x.pos)
        return positionals

    
    def remove_positional(self, query_pos: int) -> None:
        """
        removes positional and renumbers remaining positionals, flags and options
        """
        if query_pos in self.positionals:
            del self.positionals[query_pos]

        self.shift_input_positions(startpos=query_pos, amount=-1)


    def get_flags(self) -> list[Positional]:
        """
        returns list of flags in alphabetical order
        """
        flags = list(self.flags.values())
        flags.sort(key=lambda x: x.prefix)
        return flags


    def get_options(self) -> list[Positional]:
        """
        returns list of positionals in order
        """
        options = list(self.options.values())
        options.sort(key=lambda x: x.prefix.lstrip('-'))
        return options


    def set_component_positions(self) -> None:
        options_start = self.get_options_position()

        # update positionals
        self.shift_input_positions(startpos=options_start, amount=1)
        
        # update flags and opts position
        self.set_flags_options_position(options_start) 

        
    def get_options_position(self) -> int:
        # positionals will be sorted list in order of position
        # can loop through and find the first which is 
        # 'after_options' and store that int
        positionals = self.get_positionals()

        options_start = len(positionals)
        for positional in positionals:
            if positional.after_options:
                options_start = positional.pos
                break
        
        return options_start
   

    def shift_input_positions(self, startpos: int = 0, amount: int = 1) -> None:
        """
        shifts positionals position [amount] 
        starting at [startpos]
        ie if we have   inputs at 0,1,4,5,
                        shift_input_positions(2, -2)
                        inputs now at 0,1,2,3
        """
        for input_category in [self.positionals, self.flags, self.options]:
            for the_input in input_category.values():
                if the_input.pos >= startpos:
                    the_input.pos = the_input.pos + amount 

  
    def set_flags_options_position(self, new_position: int) -> None:
        for input_category in [self.flags, self.options]:
            for the_input in input_category.values():
                the_input.pos = new_position


    def __str__(self) -> str:
        out_str = ''
        out_str += '\npositionals ---------\n'
        out_str += f'{"pos":<10}{"values":40}{"gx_ref":20}{"after opts":>5}\n'
        for p in self.positionals.values():
            out_str += p.__str__() + '\n'

        out_str += '\nflags ---------------\n'
        out_str += f'{"pos":<10}{"prefix":20}{"values":40}{"gx_ref":20}\n'
        for f in self.flags.values():
            out_str += f.__str__() + '\n'

        out_str += '\noptions -------------\n'
        out_str += f'{"pos":<10}{"prefix":20}{"values":40}{"gx_ref":20}\n'
        for opt in self.options.values():
            out_str += opt.__str__() + '\n'
        
        return out_str

