
# pyright: basic

from __future__ import annotations
from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from tool.tool_definition import GalaxyToolDefinition


from command.alias.Alias import AliasRegister
from command.CommandBlock import CommandBlock

from command.tokens.Tokens import Token, TokenType
from logger.Logger import Logger

from utils.general_utils import global_align
from command.tokens.token_utils import split_line_by_ands



class CommandString:
    """
    - resolves aliases
    - breaks command into statement_blocks
    - creates command words for each statement_block
    - truncates extra command words after first pipe etc in each statement_block

    I dont like how the __init__ method is written, would rather getters
    """
    def __init__(self, command_lines: list[str], tool: GalaxyToolDefinition, logger: Logger) -> None:
        self.command_lines = command_lines
        self.tool = tool
        self.logger = logger
        self.alias_register = AliasRegister(self.tool, self.logger)
        self.command_blocks: list[CommandBlock] = []
        self.keywords = self.load_keywords()
        
        self.statement_block = -1
        self.levels = {
            'conditional': 0,
            'loop': 0
        }
        self.set_command_blocks()
        self.set_best_block()


    def load_keywords(self) -> dict[str, set[str]]:
        keywords: dict[str, set[str]] = {}
        keywords['ch_open_conditional'] = set(['#if ', '#unless '])
        keywords['ch_close_conditional'] = set(['#end if', '#end unless'])

        keywords['ch_open_loop'] = set(['#for ', '#while '])
        keywords['ch_close_loop'] = set(['#end for', '#end while'])

        keywords['cheetah_misc'] = set(['#def ', '#else if ', '#elif ', '#else', '#try ', '#except', '#end try'])
        keywords['linux'] = set(['mkdir ', 'tar ', 'ls ', 'head ', 'wget ', 'grep ', 'awk ', 'cut ', 'sed ', 'gzip ', 'gunzip ', 'cd ', 'echo ', 'trap ', 'touch '])
        keywords['alias'] = set(['set ', 'ln ', 'cp ', 'mv ', 'export ', '#set '])

        return keywords


    def set_command_blocks(self) -> None:
        active_block = self.new_block()
        cheetah_cond =      self.keywords['ch_open_conditional'] |\
                            self.keywords['ch_close_conditional'] |\
                            self.keywords['ch_open_loop'] |\
                            self.keywords['ch_close_loop']
                         
        for line in self.command_lines:
            sublines = split_line_by_ands(line)
            for sline in sublines:
                # update conditional / loop depth levels 
                self.update_cheetah_levels(sline)
                if any ([sline.startswith(kw) for kw in cheetah_cond]):
                    continue
                elif any ([sline.startswith(kw) for kw in self.keywords['alias']]):
                    self.alias_register.update(sline)
                elif not any ([sline.startswith(kw) for kw in self.keywords['cheetah_misc']]):
                    active_block = self.handle_new_line(sline, active_block)

        # add final active block to command_blocks
        self.command_blocks.append(active_block)
        self.add_block_sentinels()


    def add_block_sentinels(self) -> None:
        for block in self.command_blocks:
            end_sentinel = Token('__END__', TokenType.END_STATEMENT)
            block.tokens.append([end_sentinel])


    def handle_new_line(self, line: str, active_block: CommandBlock) -> CommandBlock:
        # do not consider anything within a for/while block
        if self.levels['loop'] == 0:
            words = get_words(line)

            for word in words:
                # this should really use the find_unquoted() method 
                # and operate on the whole line. 
                if word == '&&': 
                    self.command_blocks.append(active_block)
                    active_block = self.new_block()
                    continue
                else:
                    word = self.alias_register.template(word)
                    word = self.translate_gx_keywords(word)
                    active_block.add(word, self.levels)
        
        return active_block 


    def new_block(self) -> CommandBlock:
        self.statement_block += 1
        return CommandBlock(    
            self.statement_block, 
            self.tool.param_register,
            self.tool.out_register, 
            self.logger
        )


    def update_cheetah_levels(self, line: str) -> None:
        """updates current cheetah conditional and loop nest levels"""
        # incrementing
        for keyword in self.keywords['ch_open_conditional']:
            if line.startswith(keyword):
                self.levels['conditional'] += 1
        
        for keyword in self.keywords['ch_open_loop']:
            if line.startswith(keyword):
                self.levels['loop'] += 1

        # decrementing
        for keyword in self.keywords['ch_close_conditional']:
            if line.startswith(keyword):
                self.levels['conditional'] -= 1
        
        for keyword in self.keywords['ch_close_loop']:
            if line.startswith(keyword):
                self.levels['loop'] -= 1


    def translate_gx_keywords(self, word: str) -> str:
        gx_keywords = get_galaxy_keywords(word)
        for keyword in gx_keywords:
            kw_val = get_galaxy_keyword_value(keyword)
            word = word.replace(keyword, kw_val)

        return word
             
    
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
            best_block = 0
        
        else:
            # real block should have the most gx obj references,
            gx_ref_counts = self.get_blocks_gx_ref_count()
            
            # should start with a raw_string that is similar
            # to the main requirement
            first_token_scores = self.get_blocks_first_token_similarities()

            # decide how to use the above information
            best_block = self.choose_best_block(gx_ref_counts, first_token_scores)

        self.best_block = self.command_blocks[best_block]

        
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
        for command_block in self.command_blocks:
            first_token = command_block.tokens[0][0]
            score = global_align(self.tool.main_requirement['name'], first_token.text)
            first_token_scores_dict[command_block.statement_block] = score
        
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


    def __str__(self) -> str:
        out_str = ''
        for command_block in self.command_blocks:
            out_str += f'\nBLOCK {command_block.statement_block}\n'
            for i, token_list in enumerate(command_block.tokens):
                for token in token_list:
                    out_str += f'{i:<4}{token.type:<25}{token.text[:39]:<40}\n'
        return out_str

    
