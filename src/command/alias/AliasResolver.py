

from xmltool.tool_definition import XMLToolDefinition
from command.cmdstr.DynamicCommandStatement import DynamicCommandStatement
from command.regex.utils import split_variable_assignment, is_variable_substr, is_string_substr
from command.regex.scanners import get_simple_strings, get_custom
from command.tokens.Tokens import TokenType as tt
from command.tokens.TokenFactory import TokenFactory
from command.alias.AliasRegister import AliasRegister
import regex as re


class AliasResolver:
    def __init__(self, xmltool: XMLToolDefinition):
        self.TokenFactory = TokenFactory(tool=tool)
        self.register: AliasRegister = AliasRegister()

    def extract(self, statement: DynamicCommandStatement) -> None:
        """extracts all aliases present in the DynamicCommandStatement"""
        lines = self.get_lines(statement)
        for line in lines:
            if self.is_alias_line(line):
                self.update(line)

    def get_lines(self, statement: DynamicCommandStatement) -> list[str]:
        lines = statement.cmdline.split('\n')
        return [ln.strip() for ln in lines]
    
    def join_lines(self, lines: list[str]) -> str:
        return '\n'.join(lines)

    def is_alias_line(self, line: str) -> bool:
        alias_starts = ['#set', 'cp', 'ln']
        firstword = line.split(' ', 1)[0]
        if firstword in alias_starts:
            return True
        return False

    def update(self, line: str) -> None:
        self.update_set_aliases(line)
        self.update_symlink_aliases(line)
        self.update_copy_aliases(line)

    def update_set_aliases(self, line: str) -> None:
        """examples: #set var2 = $var1, #set $ext = '.fastq.gz'"""
        if line.startswith('#set '):
            # split the line at the operator and trim
            left, right = split_variable_assignment(line)
            left = left[5:] # removes the '#set ' from line start
            self.update_aliases(left, right, line)

    def update_symlink_aliases(self, line: str) -> None:
        """example: ln -sf '$file_input' input.fasta"""
        if line.startswith('ln '):
            left, right = line.split(' ')[-2:]
            # for ln syntax where only FILE is given (no DEST)
            if left.startswith('-'):
                left = right
            self.update_aliases(right, left, line)  # note the ordering

    def update_copy_aliases(self, line: str) -> None:
        """example: cp busco_galaxy/short_summary.*.txt BUSCO_summaries/"""
        if line.startswith('cp '):
            left, right = line.split(' ')[-2:]
            self.update_aliases(right, left, line)  # note the ordering

    def string_is_polite(self, text: str) -> bool:
        matches = get_simple_strings(text)
        simple_strings: list[str] = [m[0] for m in matches]
        if len(simple_strings) == 1 and simple_strings[0] == text:
            return True
        return False
    
    def update_aliases(self, left: str, right: str, line: str) -> None:
        # get tokens from text
        source = self.TokenFactory.tokenify(left)
        dest = self.TokenFactory.tokenify(right)
        
        if source and dest:
            match dest.type:
                case tt.RAW_STRING | tt.QUOTED_STRING:
                    if self.string_is_polite(dest.text):
                        self.register.add(source.text, dest.text, line)
                case tt.LINUX_TEE | tt.LINUX_REDIRECT | tt.LINUX_STREAM_MERGE | \
                    tt.START_STATEMENT | tt.END_STATEMENT:
                        pass
                case _:
                    self.register.add(source.text, dest.text, line)

    def resolve(self, statement: DynamicCommandStatement) -> None:
        """resolves all words/subwords in the DynamicCommandStatement which have aliases"""
        raw_lines = self.get_lines(statement)
        resolved_lines = [self.resolve_line(ln) for ln in raw_lines]
        statement.cmdline = self.join_lines(resolved_lines)
    
    def resolve_line(self, line: str) -> str:
        if self.is_alias_line(line):
            return line

        for source in self.register.get_sources():
            matches = get_custom(fr'{source}', line)
            for m in matches:
                if not is_variable_substr(m) and not is_string_substr(m):
                    # recursive
                    line = self.template(m, line, source)
                    line = self.resolve_line(line)
        return line

    def template(self, match: re.Match[str], line: str, source: str) -> str:
        aliases = self.register.get_recursive(source)
        dest = aliases[0].dest
        return line[:match.start()] + dest + line[match.end():]









    
