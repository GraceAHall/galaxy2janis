


from collections import defaultdict
import re

from classes.params.ParamRegister import ParamRegister



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
    def __init__(self, param_register: ParamRegister):
        # parsed galaxy params. needed to resolve aliases to a param. 
        self.param_register = param_register

        # stores the aliases using alias.source as key
        # each source may actually have more than 1 alias if different dests
        self.alias_dict: dict[str, list[Alias]] = {}


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

        out = []

        # for each alias source, check if in the query string
        for source in self.alias_dict.keys():
            # get partial matches
            matches = self.get_alias_match(source, query_string)
       
            if len(matches) > 0:
                destination_values = self.resolve(source)
                for val in destination_values:
                    for m in matches:
                        supp_query_string = query_string[:m.start()] + val + query_string[m.end():]
                        out.append(supp_query_string)           
                    
        if len(out) == 0:
            out = [query_string]
        
        return out


    def get_alias_match(self, source: str, query_string: str) -> list:
        # just trust this crazy regex ok
        temp = source.replace(r'\\', r'\\\\').replace('$', '\$').replace('.', '\.')
        pattern = temp + r'(?!(\.[\w-]*\()|(\()|(\w))(?=[^\w.]|(\.(forward|reverse|ext|value|name|files_path))+[^\w]|$)'
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
            # cheetah or galaxy var
            if alias.dest.startswith('$'):
                # check if galaxy param. if so, add
                if self.param_register.get(alias.dest) is not None:
                    out.append(alias.dest)

                # sometimes its weird.
                # eg '$single_paired.paired_input.forward'
                # this is actually an attribute (forward mate pair) of $single_paired.paired_input
                # temp solution: strip common galaxy attributes and try again
                else:
                    stripped_var = self.strip_gx_attributes(alias.dest)
                    if self.param_register.get(stripped_var) is not None:
                        out.append(stripped_var)

                # recursive. resolves next link if ch or gx var
                out += self.resolve(alias.dest)
            
            # literal not var 
            else:
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