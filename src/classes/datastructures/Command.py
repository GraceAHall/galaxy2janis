




class CommandLine:
    def __init__(self, command_num: str, text: str):
        self.command_num = command_num
        self.text = text
        self.in_loop = False
        self.in_conditional = False


class Token:
    def __init__(self, token_num: str, text: str):
        self.token_num = token_num
        self.text = text


class Command:
    def __init__(self, command_lines):
        self.command_lines = command_lines
        self.tokens: dict[int, Token] = {}
        self.aliases: dict[str, str] = {}


    def process(self):
        self.set_aliases()
        self.set_tokens()
        self.set_base_word()


    def set_aliases(self) -> None:
        """
        finds all aliases in command string. 
        aliases can arise from 
            #set directives: #set var2 = var1, #set ext = '.fastq.gz'
            function calls: #set temp = $to_string($proteins)
            symbolic links:  ln -s '$in1' '$in1_name'
            file copying: cp $var1 sample.fastq
            #for directives: #for $bed in $names.beds:
            export? export TERM=vt100 (mothur_pca)

        from the above: 
        { 
            '$var1': '$var2',
            '$proteins': '$temp',
            '$in1': '$in1_name',
            '$var1': 'sample.fastq'
        }

        can query the alias dict. ie for sample.fastq, what other aliases does it have? $var1 -> sample.fastq / $var2. list these as known aliases for the param
        """
        for cmd in self.command_lines:
            if '#set ' in cmd.text:
                # 
                print()


    def set_tokens(self) -> None:
        """
        - is the token  --option=arg / -option:arg ect?
            - break into an option. 
            - next.
        - does the token start with '-'?
            - label as option
            - does the next token start with not '-'?
                - try to resolve it as a galaxy param. 
                - if possible and the param default value starts with '-'
                    - next (next token is also an option)
                - else
                    - set the next token as the option argument
        - else
            - try to resolve it as a galaxy param. 
            - if possible and the param default value starts with '-'
                - label as option
            - else
                - positional arg
        """