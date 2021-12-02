


from classes.command.CommandBlock import CommandBlock
from classes.command.CommandString import CommandString
from classes.outputs.OutputRegister import OutputRegister
from classes.params.ParamRegister import ParamRegister
from classes.command.CommandComponents import Positional, Flag, Option
from classes.command.Tokens import Token, TokenType
from utils.token_utils import split_keyval_to_best_tokens 


class Command:
    def __init__(self, param_register: ParamRegister, out_register: OutputRegister):
        self.param_register = param_register
        self.out_register = out_register
        self.positionals: dict[int, Positional] = {}
        self.flags: dict[str, Flag] = {}
        self.options: dict[str, Option] = {}
        self.base_command: list[str] = []


    def update(self, command_string: CommandString) -> None:
        """
        providing a list of tokens allows the command to be updated with new info.
        the list of tokens could be from initial tool xml parsing, or from
        templated command line strings passed through galaxy tool evaluation engine.
        """
        # iterate through command words (with next word for context)
        command_block = command_string.best_block

        i = 0
        while i < len(command_block.tokens) - 1:
            curr_tokens = command_block.tokens[i]
            next_tokens = command_block.tokens[i+1]
            should_skip_next = False

            for ctoken in curr_tokens:  
                # kv pair handling. add as option with correct delim. 
                if ctoken.type == TokenType.KV_PAIR: 
                    ctoken, ntoken, delim = split_keyval_to_best_tokens(ctoken, self.param_register, self.out_register)
                    self.update_options(ctoken, ntoken, delim=delim)
                    continue

                # everything else
                for ntoken in next_tokens:
                    skip_next = self.update_components(ctoken, ntoken)
                    if skip_next:
                        should_skip_next = True
            
            if should_skip_next:
                i += 2
            else:
                i += 1


    def update_input_positions(self) -> None:
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


    def update_components(self, ctoken: Token, ntoken: Token) -> None:
        skip_next = False
        
        # first linux '>' to stdout
        if self.is_stdout(ctoken, ntoken):
            self.update_outputs(ntoken)
            skip_next = True

        # flag
        elif self.is_flag(ctoken, ntoken):
            self.update_flags(ctoken)

        # option
        elif self.is_option(ctoken, ntoken):
            self.update_options(ctoken, ntoken)
            skip_next = True

        else:
            # text positional
            # this has to happen last, as last resort
            # some examples of options which don't start with '-' exist. 
            self.update_positionals(ctoken)  

        return skip_next 


    def is_stdout(self, ctoken: Token, ntoken: Token) -> bool:
        """
        """
        if ctoken.type == TokenType.LINUX_OP:
            if ntoken.type in [TokenType.RAW_STRING, TokenType.GX_OUT]:
                return True
        return False             


    def update_outputs(self, token: Token) -> None:
        if token.type == TokenType.GX_OUT:
            output_var, output = self.out_register.get(token.text)

        elif token.type == TokenType.RAW_STRING:
            output_var, output = self.out_register.get_by_filepath(token.text, allow_nopath=True)

        if output is None:
            token.text = token.text.lstrip('$')
            self.out_register.create_output_from_text(token.text)
            # the following line is kinda bad. dollar sign shouldnt be here really...this will cause issues
            output_var, output = self.out_register.get(token.text)

        output.is_stdout = True


    def update_positionals(self, token: Token) -> None:
        key = token.text

        if key not in self.positionals:
            is_after_options = self.has_options()
            pos = self.get_positional_count()
            new_positional = Positional(pos, token, is_after_options)
            self.positionals[key] = new_positional


    def update_flags(self, token: Token) -> None:
        key = token.text

        # make entry if not exists
        if key not in self.flags:
            new_flag = Flag(key)
            self.flags[key] = new_flag
                
        self.flags[key].sources.append(token)       


    def are_identical_tokens(self, token1: Token, token2: Token) -> bool:
        if token1.text == token2.text:
            if token1.gx_ref == token2.gx_ref:
                return True
        return False


    def update_options(self, ctoken: Token, ntoken: Token, delim=' ') -> None:
        key = ctoken.text

        if key not in self.options:
            new_option = Option(key, delim)
            self.options[key] = new_option
            
        self.options[key].sources.append(ntoken)


    def is_kv_pair(self, ctoken: Token) -> bool:
        """
        https://youtu.be/hqVJpfFkJ9k
        """
        if ctoken.type == TokenType.KV_PAIR:
            return True
        return False


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


    def get_positional_count(self) -> int:
        return len(self.positionals)


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

        for positional in self.positionals.values():
            if positional.pos == query_pos:
                key_to_delete = positional.token.text
                break
        
        del self.positionals[key_to_delete]

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


    def has_options(self) -> bool:
        if len(self.flags) != 0 or len(self.options) != 0:
            return True
        return False
   

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


    def pretty_print(self) -> None:
        print('\npositionals ---------\n')
        print(f'{"pos":<10}{"text":20}{"gx_ref":20}{"token":20}{"datatype":20}{"after opts":>5}')
        for p in self.positionals.values():
            print(p)

        print('\nflags ---------------\n')
        print(f'{"text":30}{"gx_ref":30}{"token":20}{"datatype":20}{"cond":>5}')
        for f in self.flags.values():
            print(f)

        print('\noptions -------------\n')
        print(f'{"prefix":30}{"text":30}{"gx_ref":30}{"token":20}{"datatype":20}{"cond":>5}')
        for opt in self.options.values():
            print(opt)


   