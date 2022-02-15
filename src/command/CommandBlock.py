




from command.alias.AliasOld import AliasRegister
from command.tokens.Tokens import Token, TokenType
from tool.param.ParamRegister import ParamRegister
from tool.param.OutputRegister import OutputRegister
from logger.Logger import Logger
from utils import general_utils

from command.tokens.utils import tokenify



class CommandBlock:
    """
    TODO comment here
    """
    def __init__(self, statement_block: int, param_register: ParamRegister, out_register: OutputRegister, logger: Logger) -> None:
        self.statement_block = statement_block
        self.param_register = param_register
        self.out_register = out_register
        self.logger = logger
        self.tokens: list[list[Token]] = []


    def add(self, word: str, levels: dict[str, int]) -> None:
        # tokenise
        tokens = self.init_tokens(word)

        # add conditional labels
        for token in tokens:
            if levels['conditional'] > 0:
                token.in_conditional = True
            if levels['loop'] > 0:
                token.in_loop = True

        self.tokens.append(tokens)

    
    def init_tokens(self, word: str) -> Token:
        token = tokenify(word, param_register=self.param_register, out_register=self.out_register)
        
        # possibly split token if GX_INPUT is hiding flags or options
        if token.type == TokenType.GX_INPUT:
            tokens = self.expand_galaxy_tokens(token)
        else:
            tokens = [token]

        return tokens


    def get_galaxy_ref_count(self) -> int:
        galaxy_token_types = [TokenType.GX_INPUT, TokenType.GX_OUTPUT, TokenType.GX_KEYWORD]
        count = len([t for tl in self.tokens for t in tl if t.type in galaxy_token_types])
        return count


    def get_tokens(self) -> list[Token]:
        cutoff = self.get_first_command_end()
        tokens = self.tokens[:cutoff]
        # sentinel
        tokens.append([Token('__END_STATEMENT__', self.statement_block, TokenType.END_STATEMENT)])
        return tokens


    def get_first_command_end(self) -> int:
        first_command_complete = False

        for i, realised_tokens in enumerate(self.tokens):
            token = realised_tokens[0]
            if token.text == '>':
                if first_command_complete:
                    return i
                else:
                    first_command_complete = True

            elif token.text == '|':
                if not first_command_complete:
                    self.logger.log(1, "pipe encountered as end of 1st command")
                return i
        
        return i


    def expand_galaxy_tokens(self, token: Token) -> list[Token]:
        """
        expands each individual token into a list of tokens
        most commonly will just be list with single item (the original token)
        sometimes will be multiple tokens

        reason is that some galaxy select or bool params hide flags or options as their possible values

        every BoolParam will have 1+ 'realised_values'
        each SelectParam which is a list of flags / opts will have 1+ realised values

        """
        out_tokens: list[Token] = []

        values = self.param_register.get_realised_values(token.gx_ref)
        values = [v for v in values if v != '']

        if self.should_expand(values):
            for val in values:
                # in case its something like '-read_trkg yes'
                if val.startswith('-') and len(val.split(' ')) == 2:
                    new_token = Token(val, token.statement_block, TokenType.KV_PAIR)

                # else its a single word or a quoted phrase TODO CHECK THIS
                else:
                    new_token = tokenify(val, param_register=self.param_register, out_register=self.out_register)
                
                # transfer properties
                new_token.in_conditional = token.in_conditional
                new_token.in_loop = token.in_loop
                new_token.gx_ref = token.gx_ref
                out_tokens.append(new_token)
        else:
            out_tokens.append(token)
                        
        return out_tokens


    def should_expand(self, values: list[str]) -> bool:
        if len(values) == 0:
            return False

        elif all([v == '' for v in values]):
            return False
    
        for val in values:
            if not val == "" and not val.startswith('-'):
                return False

        return True


    def get_first_token_similarity(self, main_req_name: str) -> float:
        return general_utils.global_align(main_req_name, self.tokens[0].text)


    def __str__(self) -> str:
        out_str = f'\nblock {self.statement_block}\n'
        for i, realised_tokens in enumerate(self.tokens):
            for token in realised_tokens:
                out_str += f'{i:<5}{token.type:<30}{token.text}\n'
        return out_str
