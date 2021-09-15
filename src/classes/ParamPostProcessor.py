

#pyright: basic

from collections import defaultdict
from classes.datastructures.Params import Param


class ParamPostProcessor:
    def __init__(self, params: list[Param]):
        self.params = params


    def remove_duplicate_params(self) -> None:
        # TODO split into 3 functions
        param_dict: dict[str, list[Param]] = defaultdict(list)

        # name + prefix are used as key
        for query in self.params:
            key = query.name + (query.prefix or '')
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
            assert(query.name == param.name)
            assert(query.prefix == param.prefix)
            assert(query.datatype == param.datatype)
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


   