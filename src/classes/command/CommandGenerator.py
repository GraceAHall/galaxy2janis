
# pyright: basic


from typing import Optional, Tuple, Union

from classes.command.Tokens import Token, TokenType, Command
from classes.logging.Logger import Logger
from classes.outputs.OutputRegister import OutputRegister
from classes.params.ParamRegister import ParamRegister

from utils.token_utils import get_best_token
from utils.general_utils import global_align
from utils.regex_utils import find_unquoted


class CommandGenerator:
    """
    TODO comment here
    """
    


    def generate(self) -> None:
        self.select_best_block()
        self.set_command()
        self.update_input_positions()
        return self.command


    


    def set_command(self, command_tokens: list[Token]) -> Command:
        """
        goes through the tokens to work out command structure
        looks ahead to resolve difference between flag and opt with arg etc

        """
        self.command = Command(self.best_block)



        