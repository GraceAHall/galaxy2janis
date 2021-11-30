

from typing import Tuple
from classes.command.AliasExtractor import AliasExtractor
from classes.command.CommandBlock import CommandBlock

from classes.command.Tokens import TokenType
from classes.logging.Logger import Logger
from classes.tool.Tool import Tool

from utils.general_utils import global_align
from utils.regex_utils import get_galaxy_keyword_value, get_galaxy_keywords, get_words
from utils.token_utils import split_line_by_ands



class CommandString:
    """
    - resolves aliases
    - breaks command into statement_blocks
    - creates command words for each statement_block
    - truncates extra command words after first pipe etc in each statement_block
    """
    def __init__(self, command_lines: list[str], tool: Tool, logger: Logger) -> None:
        self.command_lines = command_lines
        self.tool = tool
        self.logger = logger
        self.command_blocks: list[CommandBlock] = []
        self.keywords = self.get_keywords()
        self.set_aliases()
        self.expand_aliases()
        self.translate_gx_keywords()
        self.set_command_blocks()
        self.set_best_block()


    def get_keywords(self) -> None:
        conditional_keywords = ['#if ', '#else if ', '#elif ', '#else', '#end if', '#unless ', '#end unless']
        loop_keywords = ['#for ', '#end for', '#while ', '#end while']
        error_keywords = ['#try ', '#except', '#end try']
        cheetah_var_keywords = ['#def ', '#set ']
        linux_commands = ['set ', 'ln ', 'cp ', 'mkdir ', 'tar ', 'ls ', 'head ', 'wget ', 'grep ', 'awk ', 'cut ', 'sed ', 'export ', 'gzip ', 'gunzip ', 'cd ', 'echo ', 'trap ', 'touch ']
        return conditional_keywords + loop_keywords + error_keywords + cheetah_var_keywords + linux_commands


    def set_aliases(self) -> None:
        ae = AliasExtractor(self.command_lines, self.tool, self.logger)
        ae.extract()
        self.alias_register = ae.alias_register


    def expand_aliases(self) -> None:
        out_lines: list[str] = []

        for line in self.command_lines:
            expanded_line = []
            for word in line.split():
                expanded_word = self.alias_register.template(word)
                expanded_line.append(expanded_word)
            out_lines.append(' '.join(expanded_line))

        self.command_lines = out_lines


    def translate_gx_keywords(self) -> None:
        out_lines: list[str] = []

        for line in self.command_lines:
            translated_line = []
            for word in line.split():
                gx_keywords = get_galaxy_keywords(word)
                for keyword in gx_keywords:
                    kw_val = get_galaxy_keyword_value(keyword)
                    word = word.replace(keyword, kw_val)
                translated_line.append(word)
            out_lines.append(' '.join(translated_line))

        self.command_lines = out_lines


    def set_command_blocks(self) -> None:
        self.statement_block = 0
        self.levels = {
            'if': 0,
            'unless': 0,
            'for': 0,
            'while': 0,
        }

        active_block = self.new_block()

        for line in self.command_lines:
            # update conditional depth levels 
            self.update_levels(line)
            sublines = split_line_by_ands(line) 

            for sline in sublines:
                # do not include anything within a for/while block
                if self.levels['for'] == 0 and self.levels['while'] == 0:
                    if not any([sline.startswith(kw) for kw in self.keywords]):
                        
                        words = get_words(sline)  
                        for word in words:
                            if word == '&&' or word == ';':
                                self.command_blocks.append(active_block)
                                active_block = self.new_block()
                                continue
                            else:
                                active_block.add(word, self.levels)

        # add final active block to command_blocks
        self.command_blocks.append(active_block)


    def new_block(self) -> CommandBlock:
        return CommandBlock(    
            self.statement_block, 
            self.tool.param_register,
            self.tool.out_register, 
            self.logger
        )


    def update_levels(self, line: str) -> None:
        # incrementing
        if line.startswith('#if '):
            self.levels['if'] += 1
        if line.startswith('#unless '):
            self.levels['unless'] += 1
        if line.startswith('#for '):
            self.logger.log(1, 'for loop encountered')
            self.levels['for'] += 1
        if line.startswith('#while '):
            self.logger.log(1, 'for loop encountered')
            self.levels['while'] += 1

        # decrementing
        if '#end if' in line:
            self.levels['if'] -= 1
        if '#end unless' in line:
            self.levels['unless'] -= 1
        if '#end for' in line:
            self.levels['for'] -= 1
        if '#end while' in line:
            self.levels['while'] -= 1
     
    
    def set_best_block(self) -> None:
        """
        choose how to resolve best block.
        uses number of gx obj references and the first token
        to identify the best block. 
        """
        if len(self.command_blocks) == 0:
            self.logger.log(2, 'no command block found')

        # single command block
        if len(self.command_blocks) == 1:
            return self.command_blocks[0]
        
        # real block should have the most gx obj references,
        gx_ref_counts = self.get_blocks_gx_ref_count()
        
        # should start with a raw_string that is similar
        # to the main requirement
        first_token_scores = self.get_blocks_first_token_similarities()

        # decide how to use the above information
        best_block = self.choose_best_block(gx_ref_counts, first_token_scores)

        return self.command_blocks[best_block]

        
    def get_blocks_gx_ref_count(self) -> list[Tuple[int, int]]:
        """
        for each command block, tallies the number of galaxy and kv_pair tokens
        idea is that the real command will have the most references to galaxy objs
        """
        counts = [[b.statement_block, b.get_galaxy_ref_count()] for b in self.command_blocks]
        counts.sort(key=lambda x: x[1], reverse=True)
        return counts


    def get_blocks_first_token_similarities(self) -> list[Tuple[int, float]]:
        first_token_scores_dict = {}
        for statement_block, cmd_tokens in self.command_blocks.items():
            first_token_scores_dict[statement_block] = 0
            first_token = cmd_tokens[0][0]
            score = global_align(self.tool.main_requirement['name'], first_token.text)
            first_token_scores_dict[statement_block] = score
        
        # sort by align score and return best
        first_token_scores = list(first_token_scores_dict.items())
        first_token_scores.sort(key=lambda x: x[1], reverse=True)
        return first_token_scores


    def choose_best_block(self, gx_token_tallies: list[Tuple[int, int]], first_token_scores: list[Tuple[int, float]]) -> int:

        # condition 1: 
        # gx ref based
        # one block has at least 4 gx tokens and is 2x second highest
        if gx_token_tallies[0][1] >= 4:
            if gx_token_tallies[0][1] >= 2 * gx_token_tallies[1][1]:
                return gx_token_tallies[0][0]

        # condition 2: 
        # first token similarity to main_requirement and gx token tally
        # all first tokens which have 80% of max possible alignment score
        # (usually 1) then sort by gx token count
        perfect_score = global_align(self.tool.main_requirement['name'], self.tool.main_requirement['name']) 
        filtered_blocks = [b for b, s in first_token_scores if s > 0.8 * perfect_score]
        if len(filtered_blocks) > 0:
            token_tallies = [item for item in gx_token_tallies if item[0] in filtered_blocks]
            token_tallies.sort(key=lambda x: x[1], reverse=True)
            return token_tallies[0][0]

        # condition 3:
        # highest first token score is at least half of max possible alignment score
        # and is 2x second highest score
        if first_token_scores[0][1] > 0.5 * perfect_score:
            if first_token_scores[0][1] >= 2 * first_token_scores[1][1]: 
                return first_token_scores[0][0]

        # condition 4: (fallback) return block with most gx tokens
        return gx_token_tallies[0][0]

    
