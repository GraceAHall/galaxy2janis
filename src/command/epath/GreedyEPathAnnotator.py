

from abc import ABC, abstractmethod
from typing import Any

from command.components.inputs.Flag import Flag
from command.components.inputs.Option import Option
from command.components.inputs.Positional import Positional

from command.epath.ExecutionPath import EPathPosition, ExecutionPath
from xmltool.tool_definition import XMLToolDefinition
from command.tokens.Tokens import TokenType

from command.Command import Command
import command.epath.utils as component_utils
import command.regex.scanners as scanners

"""
iterates through a ExecutionPath, yielding the current tokens being assessed.
keeps track of the location we are in the ExecutionPath

Example ExecutionPath:
abricate $sample_name --no-header --minid=80 --db = card

0            1             2            3           4          5        6           7          8
abricate     $sample_name  --no-header  --minid     =          80       --db        =          card
RAW_STRING   ENV_VAR       RAW_STRING   RAW_STRING  KV_LINKER  RAW_INT  RAW_STRING  KV_LINKER  RAW_STRING
positional1  positional2   flag1        option1     option1    option1  option2     option2    option2

at token 2, we would return {
    ctoken: token 2  (--no-header's token),
    ntokens: []
}
at token 3, we would return {
    ctoken: token 3 (--minid's token),
    ntokens: [token 4, token 5]
}

"""


class Annotator(ABC):
    """extracts a command component at the current position in an epath"""

    def __init__(self, ptr: int, positions: list[EPathPosition]):
        self.ptr = ptr
        self.positions = positions

        self.ctoken = self.positions[self.ptr].token
        self.ntoken = self.positions[self.ptr + 1].token
        self.success: bool = False

    def annotate(self) -> None:
        if self.passes_check():
            self.handle()
            self.success = True

    def update_epath_components(self, ptr: int, component: Any) -> None:
        self.positions[ptr].ignore = True
        self.positions[ptr].component = component

    @abstractmethod
    def passes_check(self) -> bool:
        """confirm whether this type of component should be extracted at the current position"""
        ...
    
    @abstractmethod
    def handle(self) -> None:
        """perform the necessary operations now that the component is valid"""
        ...
   
    @abstractmethod
    def calculate_next_ptr_pos(self) -> int:
        """update the ptr pos to continue iteration. based on component span"""
        ...
    

class OptionAnnotator(Annotator):
    """this one is complex, others are straightforward"""
    def __init__(self, ptr: int, positions: list[EPathPosition]):
        super().__init__(ptr, positions)
        self.stop_ptr: int = 0

    def passes_check(self) -> bool:
        if component_utils.is_option(self.ctoken, self.ntoken):
            if not component_utils.has_compound_structure(self.ctoken):
                return True
        return False
    
    def handle(self) -> None:
        component = Option(
            prefix=self.ctoken.text,
            delim=self.get_delim(),
            values=self.get_option_values()
        )
        for pos in range(self.ptr, self.stop_ptr + 1):
            self.update_epath_components(pos, component)

    def get_delim(self) -> str:
        if self.positions[self.ptr + 1].token.type == TokenType.KV_LINKER:
            return self.positions[self.ptr].token.text
        return ' ' # fallback default

    def get_option_values(self) -> list[str]:
        if self.is_kv_pair():
            return self.get_single_value()
        else:
            return self.get_multiple_values()

    def is_kv_pair(self) -> bool:
        if self.positions[self.ptr + 1].token.type == TokenType.KV_LINKER:
            return True
        return False
     
    def get_single_value(self) -> list[str]:
        self.stop_ptr = self.ptr + 1
        value = self.positions[self.ptr + 2]
        return [value.token.text]

    def get_multiple_values(self) -> list[str]:
        out: list[str] = []

        # define a max possible end point to consume upto (handles edge cases)
        final_pos = self.get_greedy_consumption_end()  
        values_type = self.positions[self.ptr + 1].token.type

        # look at next ntoken to see its probably a value for the option
        curr_pos = self.ptr + 1
        while curr_pos < final_pos:
            if self.should_eat_value(curr_pos, values_type):
                out.append(self.positions[curr_pos].token.text)
                curr_pos += 1 
            else:
                self.stop_ptr = curr_pos
                break
        return out

    def should_eat_value(self, curr_pos: int, values_type: TokenType) -> bool:
        ctoken = self.positions[curr_pos].token
        ntoken = self.positions[curr_pos + 1].token
        if component_utils.is_positional(ctoken) and ctoken.type == values_type and ntoken.type != TokenType.KV_LINKER:
            return True
        return False

    def get_greedy_consumption_end(self) -> int:
        """
        define an end point -> tee or redirect or end of positions
        most cases: end point = len(positions) to the end, first tee, first redirect etc - 2
        special case: 2nd last position. --files $input1 set end point = the above - 1
        """
        final_pos = self.get_end_token_position()
        if self.ptr < final_pos - 1:
            final_pos -= 1
        return final_pos

    def get_end_token_position(self) -> int:
        end_tokens = [TokenType.END_STATEMENT, TokenType.LINUX_TEE, TokenType.LINUX_REDIRECT]
        for position in self.positions:
            if position.token.type in end_tokens:
                return position.ptr - 1
        return len(self.positions) - 2  # this will never happen
    
    def calculate_next_ptr_pos(self) -> int:
        return self.stop_ptr + 1


class CompoundOptionAnnotator(Annotator):

    def passes_check(self) -> bool:
        if component_utils.is_option(self.ctoken, self.ntoken):
            if component_utils.has_compound_structure(self.ctoken):
                return True
        return False
    
    def handle(self) -> None:
        match = scanners.get_compound_opt(self.ctoken.text)[0]
        component = Option(
            prefix=match.group(1),
            delim='',
            values=[match.group(2)]
        )
        self.update_epath_components(self.ptr, component)
    
    def calculate_next_ptr_pos(self) -> int:
        return self.ptr + 1


class FlagAnnotator(Annotator):

    def passes_check(self) -> bool:
        if component_utils.is_flag(self.ctoken, self.ntoken):
            return True
        return True
    
    def handle(self) -> None:
        component = Flag(prefix=self.ctoken.text)
        self.update_epath_components(self.ptr, component)

    def calculate_next_ptr_pos(self) -> int:
        return self.ptr + 1


class PositionalAnnotator(Annotator):

    def passes_check(self) -> bool:
        if component_utils.is_positional(self.ctoken):
            return True
        return False
    
    def handle(self) -> None:
        component = Positional(value=self.ctoken.text)
        self.update_epath_components(self.ptr, component)
    
    def calculate_next_ptr_pos(self) -> int:
        return self.ptr + 1


# annotation order matters ?
annotators = [
    OptionAnnotator,   # priority 1?
    CompoundOptionAnnotator,
    FlagAnnotator,
    PositionalAnnotator
]


class GreedyEPathAnnotator:
    def __init__(self, epath: ExecutionPath, xmltool: XMLToolDefinition, command: Command):
        self.epath = epath 
        self.xmltool = xmltool
        self.command = command
        self.ptr = 0

    def annotate_epath(self) -> ExecutionPath:
        self.mark_ignore_tokens()
        self.annotate_via_param_args()
        self.annotate_via_iteration()
        self.transfer_gxparams()
        return self.epath

    def mark_ignore_tokens(self) -> None:
        ignore_tokens = [
            TokenType.FUNCTION_CALL,
            TokenType.BACKTICK_SHELL_STATEMENT,
        ]
        for position in self.epath.positions:
            if position.token.type in ignore_tokens:
                position.ignore = True
        
    def annotate_via_param_args(self) -> None:
        arguments: list[str] = [param.argument for param in self.xmltool.list_inputs() if param.argument]
        for arg in arguments:
            self.ptr = 0 # reset
            while self.ptr < len(self.epath.positions) - 1:
                token = self.epath.positions[self.ptr].token
                if token.text == arg:
                    token.type = TokenType.FORCED_PREFIX
                    self.annot()
                self.ptr += 1
    
    def annotate_via_iteration(self) -> None:
        self.ptr = 0 # reset
        while self.ptr < len(self.epath.positions) - 1:
            position = self.epath.positions[self.ptr]
            if not position.ignore:
                self.annot()
            self.ptr += 1  # ????

    def annot(self) -> None:
        for annotator in annotators:
            a = annotator(self.ptr, self.epath.positions)
            a.annotate()
            if a.success:
                self.ptr = a.calculate_next_ptr_pos()
                break

    def transfer_gxparams(self) -> None:
        for position in self.epath.positions:
            if position.component and position.token.gxparam:
                position.component.gxparam = position.token.gxparam

    
    # # this is challenging logic and ugly
    # def annot_old(self) -> None:
    #     """
    #     annotates the current epath position with a command component
    #     if position looks like an option, greedily consumes next positions 
    #     (option value can be an array) 
    #     """
    #     start = deepcopy(self.ptr) # current position we are looking at
    #     ctoken = self.epath.positions[self.ptr].token
    #     ntoken = self.epath.positions[self.ptr + 1].token

    #     ctype: str = ''
    #     delim: str = ' ' # this is really bad because it defines the default delim! should be on the option class not here.
    #     vtokens: list[Token] = []

    #     if component_utils.is_option(ctoken, ntoken):
    #         ctype= 'option'
    #         if component_utils.has_compound_structure(ctoken):
    #             delim, vtokens = self.format_compound_option()
    #         else:
    #             delim, vtokens = self.format_option()
    #     elif component_utils.is_flag(ctoken, ntoken):
    #         ctype= 'flag'
    #     else:
    #         ctype= 'positional'

    #     stop = self.ptr + 1
    #     component = spawn_component(
    #         comp_type=ctype, 
    #         ctext=ctoken.text, 
    #         ntexts=[token.text for token in vtokens], 
    #         delim=delim
    #     )
    #     self.transfer_gxparam_to_component(start, stop, component)
    #     self.update_epath(start, stop, component)

    # def format_compound_option(self) -> Tuple[str, list[Token]]:
    #     # ugly. whole module needs refactor.
    #     ctoken = self.epath.positions[self.ptr].token
    #     compound_opts = scanners.get_compound_opt(ctoken.text)

    #     match = compound_opts[0]
    #     prefix = match.group(1)
    #     prefix_match = scanners.get_all(prefix)[0]
    #     value = match.group(2)
    #     value_match = scanners.get_all(value)[0]
        
    #     ctoken.match = prefix_match                         # changes -k19 -> -k
    #     ntoken = Token(value_match, TokenType.RAW_NUM)      # generates the ntoken (the opt value)
    #     ntoken.gxparam = ctoken.gxparam
    #     delim = ''                                          # sets zero space delim
    #     return delim, [ntoken]                                           

    # def format_option(self) -> Tuple[str, list[Token]]:
    #     delim = self.get_delim()
    #     value_tokens = self.get_option_values()
    #     return delim, value_tokens

    # def get_delim(self) -> str:
    #     if self.epath.positions[self.ptr + 1].token.type == TokenType.KV_LINKER:
    #         self.ptr += 1
    #         return self.epath.positions[self.ptr].token.text
    #     return ' '

    # def get_option_values(self) -> list[Token]:
    #     if self.is_kv_pair():
    #         return self.get_single_value()
    #     else:
    #         return self.get_multiple_values()

    # def is_kv_pair(self) -> bool:
    #     if self.epath.positions[self.ptr].token.type == TokenType.KV_LINKER:
    #         return True
    #     return False
     
    # def get_single_value(self) -> list[Token]:
    #     self.ptr += 1
    #     ntoken = self.epath.positions[self.ptr].token
    #     return [ntoken]

    # def get_multiple_values(self) -> list[Token]:
    #     out: list[Token] = []

    #     # define a max possible end point to consume upto (handles edge cases)
    #     final_pos = self.get_greedy_consumption_end()  
    #     values_type = self.epath.positions[self.ptr + 1].token.type

    #     # look at next ntoken to see its probably a value for the option
    #     while self.ptr < final_pos:
    #         ntoken = self.epath.positions[self.ptr + 1].token
    #         nntoken = self.epath.positions[self.ptr + 2].token

    #         if component_utils.is_positional(ntoken) and ntoken.type == values_type and nntoken.type != TokenType.KV_LINKER:
    #             out.append(ntoken)
    #             self.ptr += 1 
    #         else:
    #             break

    #     return out

    # def get_greedy_consumption_end(self) -> int:
    #     """
    #     define an end point -> tee or redirect or end of positions
    #         most cases: end point = len(positions) to the end, first tee, first redirect etc - 2
    #         special case: 2nd last position. --files $input1 set end point = the above - 1
    #     """
    #     # general case
    #     final_pos = self.epath.get_end_token_position()
    #     # don't eat final position in cases of --mode 'fast' '$inputfile'
    #     if self.ptr < final_pos - 1:
    #         final_pos -= 1
    #     return final_pos

    # def transfer_gxparam_to_component(self, start: int, stop: int, component: CommandComponent) -> None:
    #     for i in range(start, stop):
    #         epath_gxparam = self.epath.positions[i].token.gxparam
    #         if epath_gxparam:
    #             component.gxparam = epath_gxparam
    #             break

    # def update_epath(self, start: int, stop: int, component: CommandComponent) -> None:
    #     # annotate epath positions with the discovered component (also marks them to ignore)
    #     indicies = list(range(start, stop))
    #     for index in indicies:
    #         self.epath.annotate_position_with_component(index, component)


    # def refine_component(self, component: CommandComponent) -> CommandComponent:
    #     """
    #     updates the component based on existing knowledge of the command.
    #     and example is where we think a component was an option, 
    #     but its actually a flag followed by a positional.
    #     """
    #     # cast Option to Flag
    #     if isinstance(component, Option):
    #         flags = self.command.get_flags()
    #         for flag in flags:
    #             match flag:
    #                 case Flag(prefix=component.prefix):
    #                     component = component_utils.cast_opt_to_flag(component)
    #                     break
    #                 case _:
    #                     pass
    #     return component