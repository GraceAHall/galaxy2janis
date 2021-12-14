


from __future__ import annotations
from typing import Tuple, TYPE_CHECKING
import regex as re

if TYPE_CHECKING:
    from classes.tool.Tool import Tool

from classes.logging.Logger import Logger
from classes.command.Tokens import Token, TokenType

from utils.regex_utils import find_unquoted, get_simple_strings
from utils.token_utils import tokenify


class Alias:
    def __init__(self, source: str, dest: str, instruction: str, text: str):
        self.source = source
        self.dest = dest
        self.instruction = instruction
        self.text = text


"""
AliasRegister stores the aliases we discover while parsing command string
Facilitates 
    adding new aliases to the register
    returing the aliases

This whole class needs to be written cleaner
Started with simple logic but quickly expanded
"""

class AliasRegister:
    # def __init__(self, param_register: ParamRegister, out_register: OutputRegister):
    #     # parsed galaxy objs. needed to resolve aliases 
    #     self.param_register = param_register
    #     self.out_register = out_register
    def __init__(self, tool: Tool, logger: Logger):
        # stores the aliases using alias.source as key
        # each source may actually have more than 1 alias if different dests
        self.tool = tool
        self.logger = logger
        self.alias_dict: dict[str, list[Alias]] = {}


    def update(self, line: str) -> None:
        """extracts alias if possible from line and updates register. """
        self.update_set_aliases(line)
        self.update_symlink_aliases(line)
        self.update_copy_aliases(line)
            
          
    def update_set_aliases(self, line: str) -> None:
        """
        examples:
        #set var2 = $var1
        #set $ext = '.fastq.gz'
        """
        if line.startswith('#set '):
            # split the line at the operator and trim
            left, right = self.split_variable_assignment(line)
            left = left[5:] # removes the '#set ' from line start
            self.update_aliases(left, right, 'set', line)  


    def split_variable_assignment(self, line: str) -> Tuple[str, str]:
        operator_pattern = r'[-+\\/*=]?='
        #print('\n' + line)

        operator_start, operator_end = find_unquoted(line, operator_pattern)
        left, right = line[:operator_start].strip(), line[operator_end:].strip()
        return left, right

            
    def update_aliases(self, source_text: str, dest_text: str, from_cmd: str, line: str) -> None:
        # get tokens from text
        
        if not self.is_phrase(dest_text):
            source = self.init_token_from_text(source_text)
            dest = self.init_token_from_text(dest_text)

            # update
            if source is not None and dest is not None:
                # destination is a know galaxy object
                if dest.type in [TokenType.GX_OUT, TokenType.GX_PARAM]:
                    self.add(source.text, dest.text, from_cmd, line)

                # destination is a number
                elif dest.type in [TokenType.RAW_NUM, TokenType.QUOTED_NUM]:
                    self.add(source.text, dest.text, from_cmd, line)

                # destination is a string but its very simple looking
                elif dest.type in [TokenType.RAW_STRING, TokenType.QUOTED_STRING]:
                    if self.string_is_polite(dest.text):
                        self.add(source.text, dest.text, from_cmd, line)

        else:
            self.logger.log(1, f'could not add alias from line: {line}')


    def is_phrase(self, the_string: str) -> bool:
        word_break_start, _ = find_unquoted(the_string, ' ')
        if word_break_start != -1:
            return True
        return False


    def init_token_from_text(self, text: str) -> Token:
        token = tokenify(text, param_register=self.tool.param_register, out_register=self.tool.out_register, prioritise_tokens=False)
        if token == None:
            self.logger.log(1, f'can resolve token {text}')
        return token


    def string_is_polite(self, text: str) -> bool:
        simple_strings = get_simple_strings(text)
        if len(simple_strings) == 1 and simple_strings[0] == text:
            return True
        return False

    
    def add(self, source: str, dest: str, instruction: str, text: str) -> None:
        # check its not referencing itself
        if source != dest:
            alias = Alias(source, dest, instruction, text)
            
            if alias.source not in self.alias_dict:
                self.alias_dict[alias.source] = []

            known_aliases = self.alias_dict[alias.source]
            if not any([dest == al.dest for al in known_aliases]):
                # if valid, create new alias and store
                self.alias_dict[alias.source].append(alias)


    def update_symlink_aliases(self, line: str) -> None:
        """
        NOTE - dest and source are swapped for symlinks.
        """
        if line.startswith('ln '):
            left, right = line.split(' ')[-2:]

            # for ln syntax where only FILE is given (no DEST)
            if left.startswith('-'):
                left = right

            self.update_aliases(right, left, 'ln', line)  


    def update_copy_aliases(self, line: str) -> None:
        """
        NOTE - dest and source are swapped for cp commands.

        basically the same as symlinks, just checking if cp command in line
        handling cp commands can be tricky:

            cp '$hd5_format.in.matrix' 'mtx/matrix.mtx'
            cp -r "\$AUGUSTUS_CONFIG_PATH/" augustus_dir/
            cp busco_galaxy/short_summary.*.txt BUSCO_summaries/
            cp '$test_case_conf' circos/conf/galaxy_test_case.json
            #for $hi, $data in enumerate($sec_links.data):
                cp '${data.data_source}' circos/data/links-${hi}.txt
        """       
        if line.startswith('cp '):
            left, right = line.split(' ')[-2:]
            self.update_aliases(right, left, 'cp', line) 


    def template(self, query_string: str) -> list[str]:
        """
        given a query string, templates first var with aliases. 
        ASSUMES ONLY 1 ALIAS IN STRING. otherwise this would get a little recursive. 
        its doable, just not high priority right now

        Example behaviour:
        Aliases
            $input: file.fasta

        Galaxy params
            $input.names
        
        Function input -> output:
            $input -> file.fasta
            $input/mystuff -> file.fasta/mystuff
            $input.names -> $input.names      (not file.fasta.names)
            $input.forward (galaxy attribute) -> file.fasta.forward
        """
        # for each alias source, check if in the query string
        for source in self.alias_dict.keys():
            # get partial matches
            matches = self.get_alias_match(source, query_string)
       
            if len(matches) > 0:
                destination_values = self.resolve(source)
                for val in destination_values:
                    for m in matches:
                        query_string = query_string[:m.start()] + val + query_string[m.end():]
        
        return query_string


    def get_alias_match(self, source: str, query_string: str) -> list:
        # just trust this crazy regex ok
        temp = source.replace(r'\\', r'\\\\').replace('$', '\$').replace('.', '\.')
        pattern = temp + r'(?!(\.[\w-]*\()|(\()|(\w))(?=[^\w.]|(\.(forward|reverse|ext|value|name|files_path|element_identifier))+[^\w]|$)'
        res = re.finditer(pattern, query_string)
        matches = [m for m in res]
        return matches
        

    # deprecated
    def get_partial_matches(self, source: str, query_string: str) -> list:
        temp = source.replace(r'\\', r'\\\\').replace('$', '\$').replace('.', '\.')
        pattern = re.compile(f'{temp}(?![\w])')
        res = re.finditer(pattern, query_string)
        matches = [m for m in res]
        return matches


    # deprecated
    def filter_non_full_matches(self, matches: str, query_string: str) -> list:
        out_matches = []
        for m in matches:
            print(m[0], m.start(), m.end())

            if m.end() < len(query_string):
            #    if query_string[m.end() + 1] == '.'
            #if query_string[]
                pass
        
        return out_matches


    def resolve(self, query_var: str) -> list[str]:
        """
        returns list of all gx vars, and literals that are linked to the query_var
        cheetah vars should be fully resolved here 
        """
        out = []

        if query_var in self.alias_dict:
            aliases = self.alias_dict[query_var]
        else:
            return out

        for alias in aliases:
            out.append(alias.dest)

        return out


    def strip_gx_attributes(self, the_string: str) -> str:
        gx_attributes = set([
            '.forward',
            '.reverse',
            '.ext',
            '.value',
            '.name',
            '.files_path'
        ])
        # needs to be recursive so we can iterately peel back 
        # eg  in1.forward.ext
        # need to peel .ext then peel .forward.

        for att in gx_attributes:
            if the_string.endswith(att):
                # strip from the right - num of chars in the att
                the_string = the_string[:-len(att)]

                # recurse
                the_string = self.strip_gx_attributes(the_string)
        
        return the_string