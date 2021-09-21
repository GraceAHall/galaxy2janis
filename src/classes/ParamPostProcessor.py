

#pyright: basic

from classes.Logger import Logger

from collections import defaultdict
from classes.datastructures.Params import Param


class ParamPostProcessor:
    def __init__(self, params: list[Param], logger: Logger):
        self.params = params
        self.logger = logger


    def remove_duplicate_params(self) -> None:
        # TODO split into 3 functions
        param_dict: dict[str, list[Param]] = defaultdict(list)

        # gx_var + prefix are used as key
        for query in self.params:
            key = query.gx_var + (query.prefix or '')
            param_dict[key].append(query)

        # remove exact duplicates in each list
        for key, param_list in param_dict.items():
            unique_params = []
            for query in param_list:
                self.append_unique(query, unique_params)
            param_dict[key] = unique_params

        # user resolve if param has 2 listed datatypes 
        clean_params: list[Param] = []
        for key, param_list in param_dict.items():
            if len(param_list) > 1:
                # TEMP - stops execution rather than accepting user input to resolve
                self.logger.log(2, 'param required user input')
                param_list = self.user_resolve_datatype(param_list)
            clean_params += param_list

        self.params = clean_params


    def append_unique(self, query: Param, param_list: list[Param]) -> None:
        """
        iterate through params in param_list, check none are the same as the param to add. 
        If all ok, add the query param to param_list. 
        """
        for param in param_list:
            if self.assert_duplicate_param(query, param):
                return  # early exit if query already exists
        
        param_list.append(query)  # if query not in param_list
        

    def assert_duplicate_param(self, query: Param, param: Param) -> bool:
        try:
            assert(query.gx_var == param.gx_var)
            assert(query.prefix == param.prefix)
            assert(query.galaxy_type == param.galaxy_type)
            return True
        except AssertionError:
            return False


    def user_resolve_datatype(self, param_list: list[Param]) -> list[Param]:
        gx_var = param_list[0].gx_var
        
        # print basics
        print(f'\n--- datatype selection: {gx_var} ---')

        # print each candidate prefix
        for i, param in enumerate(param_list):
            print(i, end=' ')
            print(param)
        
        selected = int(input('Selected param [int]: '))
        return [param_list[selected]]


    def set_prefixes(self) -> None:
        """
        single occurance in cmd string (ref) usually (ignoring cheetah 
        conditional lines) 
        multiple refs need human decision.
        """
        for param in self.params:
            cmd_refs = param.cmd_references 
            cmd_refs = [ref for ref in cmd_refs if not ref.in_conditional]  
            
            if len(cmd_refs) == 1:
                param.prefix = cmd_refs[0].prefix
            elif len(cmd_refs) > 1:
                self.logger.log(2, 'param required user input')
                param.prefix = param.user_select_prefix()


    def pretty_print(self) -> None:
        print('\n--- Params ---\n')
        print(f'{"name":50}{"datatype":25}{"prefix":20}{"command":>10}')
        print('-' * 105)
        for param in self.params:
            print(param)