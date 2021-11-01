


from collections import defaultdict
import re

from classes.datastructures.Params import Param


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
    def __init__(self, params: dict[str, Param]):
        # parsed galaxy params. needed to resolve aliases to a param. 
        self.gx_params = params

        # stores the aliases using alias.source as key
        # each source may actually have more than 1 alias if different dests
        self.alias_dict: dict[str, list[Alias]] = defaultdict(list)


    def add(self, source: str, dest: str, instruction: str, text: str) -> None:
        # check its not referencing itself
        if source != dest:
            known_aliases = self.alias_dict[source]
            if not any([dest == al.dest for al in known_aliases]):
                # if valid, create new alias and store
                new_alias = Alias(source, dest, instruction, text)
                self.alias_dict[new_alias.source].append(new_alias)


    def template(self, query_string: str) -> list[str]:
        """
        given a query string, templates first var with aliases. 
        ASSUMES ONLY 1 ALIAS IN STRING. otherwise this would get a little recursive. 
        returns list of all possible forms of the query string
        """

        out = []

        for source in self.alias_dict.keys():
            # in case the var has curly braces in text
            if source.startswith('$'):
                patterns = [source, '${' + source[1:] + '}']
                patterns = [re.compile(f'\{p}(?![\w])') for p in patterns]
            else:
                patterns = [re.compile(f'{source}(?![\w])')]

            for patt in patterns:
                res = re.finditer(patt, query_string)
                matches = [m for m in res]
                if len(matches) > 0:
                    possible_values = self.resolve(source)

                    # may be multiple resolved values.
                    for val in possible_values:
                        for m in matches:
                            supp_query_string = query_string[:m.start()] + val + query_string[m.end():]
                            out.append(supp_query_string)
                    
                    return out

        return [query_string]



    def resolve(self, query_var: str) -> list[str]:
        """
        returns list of all gx vars, and literals that are linked to the query_var
        cheetah vars should be fully resolved here 
        """
        aliases = self.alias_dict[query_var]
        out = []

        for alias in aliases:
            # cheetah or galaxy var
            if alias.dest.startswith('$'):
                # add if galaxy param
                if alias.dest in self.gx_params:
                    out.append(alias.dest)

                # sometimes its weird.
                # eg '$single_paired.paired_input.forward'
                # this is actually an attribute (forward mate pair) of $single_paired.paired_input
                # temp solution: strip common galaxy attributes and try again
                else:
                    stripped_var = self.strip_gx_attributes(alias.dest)
                    if stripped_var in self.gx_params:
                        out.append(stripped_var)

                # recursive. resolves next link if ch or gx var
                out += self.resolve(alias.dest)
                print()
            
            # literal
            else:
                out.append(alias.dest)

        return out


    def strip_gx_attributes(self, the_string: str) -> str:
        gx_attributes = set([
            '.forward',
            '.reverse',
            '.ext',
            '.value',
            '.name'
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