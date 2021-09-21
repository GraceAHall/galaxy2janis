
# pyright: basic

# needs to be extensible as will expand in future
# what if the same variable is used 2 times in a line? annoying

class VariableReference:
    def __init__(self, gx_var: str, pos: int, command_line: list[str]):
        self.gx_var = gx_var
        self.pos = pos
        self.command_line = command_line.split(' ')
        self.in_conditional: bool = self.get_is_conditional()
        self.prefix: str = self.get_prefix() 

    
    def get_is_conditional(self) -> bool:
        cheetah_conditionals = ['#if', '#else', '#elif', '#end', '#while', '#return', '#import', '#def']
        
        if self.command_line[0] in cheetah_conditionals:
            return True
        return False


    def get_prefix(self) -> str:
        """
        checks if the previous word looks like a valid parameter prefix
        maybe here I will ban common linux terms
        """
        if self.pos != 0:
            prev_word = self.command_line[self.pos - 1]
            if prev_word.startswith('-'):
                return prev_word
        return ''


    def __str__(self) -> str:
        out_str = ''
        out_str += f'var: {self.gx_var}\n'
        out_str += f'command_line: {self.command_line}\n'
        out_str += f'pos: {self.pos}\n'
        out_str += f'in_conditional: {self.in_conditional}\n'
        out_str += f'prefix: {self.prefix}\n'
        return out_str



class VariableFinder:
    def __init__(self, var: str, command_lines: list[str]) -> None:
        self.gx_var = var
        self.command_lines = command_lines
        self.references: list[VariableReference] = []

        self.banned_commands = [
            'cp', 'tar', 'mkdir', 'pwd',
            'which', 'cd', 'ls', 'cat', 'mv',
            'rmdir', 'rm', 'touch', 'locate', 'find',
            'grep', 'head', 'tail', 'chmod', 'chown', 
            'wget', 'echo', 'zip', 'unzip', 'gzip',
            'gunzip', 'export'
        ]


    def find(self) -> list[VariableReference]:
        for line in self.command_lines:
            # TODO convert to list of locs incase appears 2+ times in line
            loc = self.find_param_in_line(line) 
            if loc != -1:
                new_ref = VariableReference(self.gx_var, loc, line)
                self.add_ref(new_ref)

        #self.list_refs() debugging
        return self.references
                

    def find_param_in_line(self, command_line: str) -> int:
        command_list = command_line.split(' ')
        
        for i, word in enumerate(command_list):
            if self.gx_var in word:
                if self.confirm_cheetah_var(word):
                    return i
        return -1


    def confirm_cheetah_var(self, command_word: str) -> bool:
        """
        strips cheetah var syntax to expose var as raw text
        $var '${var}' "${var}" '$var' "$var" all valid. 
        """
        # confirm quote pairs
        if command_word[0] in ['"', "'"]:
            if command_word[-1] != command_word[0]:
                return False
        command_word = command_word.strip('"').strip("'")

        # confirm begins with '$'
        # possible values at this stage: [$var, ${var}]
        if command_word[0] != '$':
            return False
        command_word = command_word.strip('$')
        
        # handle curly brackets
        # possible values at this stage: [var, {var}]
        if command_word[0] == '{':
            if command_word[-1] != '}':
                return False
        command_word = command_word.strip('{').strip('}')

        # command_word should now equal var
        if command_word != self.gx_var:
            return False
        
        return True


    def confirm_cheetah_var_future(self, command_word: str) -> bool:
        """
        future version. currently use confirm_cheetah_var. relies on the variable to appear by itself as a word (separated by ' ')
        """
        # get the match location
        start_match = command_word.find(self.gx_var)
        end_match = start_match + len(self.gx_var) - 1

        # if bracket format ${var}
        if command_word[start_match - 1] == '{':
            if command_word[end_match + 1] != '}' or command_word[start_match - 2] != '$':
                return False

        # if naked $var
        elif command_word[start_match - 1] != '$':
            return False
        
        # check doesn't follow with a '.' (should actually lookup whether any param matches better)
        elif len(command_word) > end_match + 1:
            if command_word[end_match + 1] == '.':
                return False

        return True

        


    def add_ref(self, new_ref) -> None:
        # check if identical ref already exists. not sure if this would occur. 
        for ref in self.references:
            if new_ref.command_line == ref.command_line and new_ref.prefix == ref.prefix:
                return None
        self.references.append(new_ref)


    def list_refs(self) -> None:
        for ref in self.references:
            print(ref)
    

    

