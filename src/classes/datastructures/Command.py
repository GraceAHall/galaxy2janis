




class Command:
    def __init__(self):
        self.aliases: dict[str, str] = {}



    def parse(self):
        pass





    def set_aliases(self, command_lines: list[str]) -> dict[str, str]:
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
        pass