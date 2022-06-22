



from abc import ABC, abstractmethod
from typing import Any

from shellparser.components.inputs.Flag import Flag
from shellparser.components.inputs.Option import Option
from shellparser.components.inputs.Positional import Positional

from shellparser.epath.ExecutionPath import EPathPosition
from shellparser.text.tokens.Tokens import Token, TokenType

from shellparser.components.outputs.create import create_output
from shellparser.components.linux import Tee, StreamMerge

import shellparser.epath.utils as component_utils
import shellparser.text.regex.scanners as scanners


class Annotator(ABC):

    """extracts a command component at the current position in an epath"""
    def __init__(self, ptr: int, positions: list[EPathPosition]):
        self.ptr = ptr
        self.positions = positions

        self.ctoken: Token = self.positions[self.ptr].token
        self.ntoken: Token = self.positions[self.ptr + 1].token
        self.success: bool = False

    def annotate(self) -> None:
        if self.passes_check():
            self.handle()
            self.success = True

    def update_epath_components(self, ptr: int, component: Any) -> None:
        self.positions[ptr].component = component
        self.positions[ptr].ignore = True

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
    

# --------------
# TOOL ARGUMENTS
# --------------

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
        if self.ntoken.type == TokenType.KV_LINKER:
            return self.ntoken.text
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
        # if is_kv_pair() -- self.ptr + 1 will always be KV_LINKER
        self.stop_ptr = self.ptr + 2
        value = self.positions[self.ptr + 2]
        return [value.token.text]

    def get_multiple_values(self) -> list[str]:
        out: list[str] = []

        # define a max possible end point to consume upto (handles edge cases)
        final_pos = self.get_greedy_consumption_end()  
        values_type = self.positions[self.ptr + 1].token.type

        # look at next ntoken to see its probably a value for the option
        curr_pos = self.ptr + 1
        while curr_pos <= final_pos:
            if self.should_eat_value(curr_pos, values_type):
                out.append(self.positions[curr_pos].token.text)
                curr_pos += 1 
            else:
                break
        self.stop_ptr = curr_pos - 1
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
        return False
    
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
 

# --------------
# LINUX CONSTRUCTS
# --------------

class StreamMergeAnnotator(Annotator):

    def passes_check(self) -> bool:
        if self.ctoken.type == TokenType.LINUX_STREAM_MERGE:
            return True
        return False
    
    def handle(self) -> None:
        component = StreamMerge(self.ctoken)
        self.update_epath_components(self.ptr, component)
   
    def calculate_next_ptr_pos(self) -> int:
        return self.ptr + 1


class RedirectAnnotator(Annotator):

    def passes_check(self) -> bool:
        if self.ctoken.type == TokenType.LINUX_REDIRECT:
            return True
        return False
    
    def handle(self) -> None:
        if self.ctoken and self.ntoken:  # ???
            tokens = (self.ctoken, self.ntoken)
            component = create_output('redirect', tokens)
            self.update_epath_components(self.ptr, component)
            self.update_epath_components(self.ptr + 1, component)
   
    def calculate_next_ptr_pos(self) -> int:
        return self.ptr + 2


class TeeAnnotator(Annotator):

    def passes_check(self) -> bool:
        if self.ctoken.type == TokenType.LINUX_TEE:
            return True
        return False

    def handle(self) -> None:
        tee = Tee()
        ptr = self.ptr + 1 # TODO debug -> does this change self.ptr?

        # tee arguments
        token = self.positions[ptr].token
        while token.text.startswith('-'):
            tee.options.append(token)
            self.update_epath_components(ptr, tee)
            ptr += 1
            token = self.positions[ptr].token

        # tee files: consumes to end of statement
        while ptr < len(self.positions) - 1:
            token = self.positions[ptr].token
            tee.files.append(token)
            self.update_epath_components(ptr, tee)
            ptr += 1

    def calculate_next_ptr_pos(self) -> int:
        return len(self.positions)


