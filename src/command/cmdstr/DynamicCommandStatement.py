

from copy import deepcopy
from typing import Iterable, Optional

from xmltool.tool_definition import XMLToolDefinition
from command.tokens.Tokens import Token, TokenType
from command.tokens.RealisedTokenValues import RealisedTokenValueifier, RealisedTokenValues
from command.epath.ExecutionPath import ExecutionPath
from command.regex.scanners import get_all

class DynamicCommandStatement:
    """
    represents a command line statement. 
    
    for example:
        ln -sf '${file_input}' ${sample_name} &&
        abricate ${sample_name} > '$report'
    
    in the above, there are two statements: the symlink, then the abricate command.
    these are seperated by &&.

    one of these statements will be the tool actually being executed, the other is pre/post
    processing. 
    
    each individual command line statement is represented as a DynamicCommandStatement.
    each statement can have multiple realised values, in the case of galaxy select or bool 
    params being present in that statement statement.
    """

    def __init__(self, cmdline: str, end_delim: Optional[str]=None):
        self.cmdline = cmdline
        self.end_delim = end_delim
        self.realised_tokens: list[RealisedTokenValues] = []

    def set_realised_tokens(self, xmltool: XMLToolDefinition) -> None:
        self.realised_tokens = RealisedTokenValueifier(xmltool).tokenify(self.cmdline)

    def get_tokens(self) -> list[Token]:
        tokens: list[Token] = []
        tokens += [rt.get_original_token() for rt in self.realised_tokens]
        if self.end_delim:
            match = get_all(self.end_delim)[0]
            tokens.append(Token(match, TokenType.END_STATEMENT))
        return tokens

    def get_execution_paths(self) -> Iterable[ExecutionPath]:
        """
        galaxy select or bool params may have multiple possible realised values 
        in a command string. for each of these values, we create an ExecutionPath
        which represents a possible realised command line, with a particular value 
        slotted in for that select or bool param. 
                
        Each other token becomes the default value for that position 
        (ie abricate --$input1 will always appear as Token(abricate), Token(--$input1) 
        as there are no alternatives). 
        
        For sitations where the other token is also a bool / select, we just provide 
        any realised value of that bool / select as a token. 

        each of these ExecutionPaths are fed into the program later when attempting
        to understand the tool Command()

        """ 
        # get all tokens as defaults
        default_tokens = [rtvs.get_default_token() for rtvs in self.realised_tokens]
        for i in range(len(self.realised_tokens)):
            tokens_copy = deepcopy(default_tokens)
            if len(self.realised_tokens[i].tlists) > 1:
                # get the additional different values the current position can take and 
                # hot swap these in to the default tokens to produce 'realised' tokens
                for tlist in self.realised_tokens[i].tlists[1:]:
                    realised_tokens = tokens_copy[:i] + tlist + tokens_copy[i + 1:]
                    yield ExecutionPath(realised_tokens)

        # yield the defaults as final ExecutionPath
        yield ExecutionPath(default_tokens)
    
    def get_galaxy_reference_count(self) -> int:
        default_tokens = [rtvs.get_default_token() for rtvs in self.realised_tokens]
        return sum([token.gxparam is not None for token in default_tokens])
    
    def get_first_word(self) -> str:
        return self.realised_tokens[0].tlists[0][0].text # pure cancer but 

    def print_execution_paths(self) -> None:
        for epath in self.get_execution_paths():
            for position in epath.positions:
                print(position.token.text, end=' ')
            print('\n')


