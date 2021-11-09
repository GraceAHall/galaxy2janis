


from typing import Optional


from classes.params.Params import BoolParam, Param, SelectParam


class ParamRegister:
    def __init__(self) -> None:
        self.params: dict[str, Param] = {}
        

    def add(self, params: list[Param]) -> None:
        for param in params:
            key = '$' + param.gx_var
            if key not in self.params:
                self.params[key] = param


    def get(self, query_key: str, ignore_path=False) -> Optional[Param]:
        # incase we dont care about path and just want final dot.
        if ignore_path == True:
            for key in list(self.params.keys()):
                nopath_key = key.rsplit('.')[-1]
                if nopath_key.endswith(query_key.lstrip('$')):
                    return self.params[key]

        # when we want to match full path
        else:
            if query_key in self.params:
                return self.params[query_key]

        return None


    def get_realised_values(self, query_key: str) -> list[str]:
        """
        returns list of non-blank strings representing preprogrammed values
        the variable can template to.
        only returns values for select and bool params, as only these can 
        """
        out = []
        if query_key in self.params:
            param = self.params[query_key]

            if type(param) == SelectParam:
                out = param.options
            elif type(param) == BoolParam:
                out = [param.truevalue, param.falsevalue]
                out = [o for o in out if o != '']

        return out


    def restructure_params(self, params: list[Param]) -> None:
        param_dict = {}
        for p in params:
            key = '$' + p.gx_var
            param_dict[key] = p
        self.params = param_dict


