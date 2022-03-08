

from copy import deepcopy
from typing import Tuple

from command.epath.ExecutionPath import ExecutionPath
from tool.tool_definition import GalaxyToolDefinition
from command.tokens.Tokens import Token, TokenType

from command.Command import Command
from command.components.CommandComponent import CommandComponent
from command.epath.ComponentSpawner import spawn_component
import command.epath.utils as component_utils


"""
iterates through a DynamicCommandString, yielding the current tokens being assessed.
keeps track of the location we are in the DynamicCommandString

Example DynamicCommandString:
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



class GreedyEPathAnnotator:
    def __init__(self, epath: ExecutionPath, tool: GalaxyToolDefinition, command: Command):
        self.epath = epath 
        self.tool = tool
        self.command = command
        self.pos = 0

    def annotate(self) -> ExecutionPath:
        self.annotate_via_param_args()
        self.annotate_via_iteration()
        return self.epath
        
    def annotate_via_param_args(self) -> None:
        arguments: list[str] = [param.argument for param in self.tool.list_inputs() if param.argument]
        for arg in arguments:
            self.pos = 0 # reset
            while self.pos < len(self.epath.positions) - 1:
                token = self.epath.positions[self.pos].token
                if token.text == arg:
                    self.annot()
                self.pos += 1
    
    def annotate_via_iteration(self) -> None:
        self.pos = 0 # reset
        while self.pos < len(self.epath.positions) - 1:
            position = self.epath.positions[self.pos]
            if not position.ignore:
                self.annot()
            self.pos += 1
    
    def annot(self) -> None:
        """
        annotates the current epath position with a command component
        if position looks like an option, greedily consumes next positions 
        (option value can be an array) 
        """
        start = deepcopy(self.pos) # current position we are looking at
        ctoken = self.epath.positions[self.pos].token
        ntoken = self.epath.positions[self.pos + 1].token

        ctype: str = ''
        delim: str = ' ' # this is really bad because it defines the default delim! should be on the option class not here.
        vtokens: list[Token] = []

        if component_utils.is_option(ctoken, ntoken):
            ctype= 'option'
            delim, vtokens = self.format_option()
        elif component_utils.is_flag(ctoken, ntoken):
            ctype= 'flag'
        else:
            ctype= 'positional'

        stop = self.pos + 1
        component = spawn_component(ctype, ctoken, vtokens, epath_id=self.epath.id, delim=delim)
        self.transfer_gxvar_to_component(start, stop, component)
        self.update_epath(start, stop, component)

    def format_option(self) -> Tuple[str, list[Token]]:
        delim = self.get_delim()
        value_tokens = self.get_option_values()
        return delim, value_tokens

    def get_delim(self) -> str:
        if self.epath.positions[self.pos + 1].token.type == TokenType.KV_LINKER:
            self.pos += 1
            return self.epath.positions[self.pos].token.text
        return ' '

    def get_option_values(self) -> list[Token]:
        out: list[Token] = []
        ntoken = self.epath.positions[self.pos + 1].token
        values_type = ntoken.type
        # look at next ntoken to see its probably a value for the option
        while component_utils.is_positional(ntoken) and ntoken.type == values_type:
            out.append(ntoken)
            self.pos += 1 
            if self.pos >= len(self.epath.positions) - 1:
                break
            else:
                ntoken = self.epath.positions[self.pos + 1].token
        return out

    def transfer_gxvar_to_component(self, start: int, stop: int, component: CommandComponent) -> None:
        for i in range(start, stop):
            epath_gxvar = self.epath.positions[i].token.gxvar
            if epath_gxvar:
                component.gxvar = epath_gxvar
                break

    def update_epath(self, start: int, stop: int, component: CommandComponent) -> None:
        # annotate epath positions with the discovered component (also marks them to ignore)
        indicies = list(range(start, stop))
        for index in indicies:
            self.epath.annotate_position_with_component(index, component)


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