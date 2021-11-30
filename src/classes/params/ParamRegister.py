


from typing import Optional
from copy import deepcopy


from galaxy.tools.parameters.basic import (
    ToolParameter,
    BooleanToolParameter,
    SelectToolParameter
)


class ParamRegister:
    def __init__(self, inputs: dict) -> None:
        self.params: dict[str, ToolParameter] = {}
        self.add_from_dict(inputs, [])
        print()
        

    def add_from_dict(self, inputs: dict, levels: list[str]) -> None:
        for label, obj in inputs.items():
            if hasattr(obj, 'inputs'):
                next_levels = deepcopy(levels)
                next_levels.append(obj.name)
                self.add_from_dict(obj.inputs, next_levels)

            elif hasattr(obj, 'cases'):
                next_levels = deepcopy(levels)
                next_levels.append(obj.name)
                self.add_param(obj.test_param, next_levels)
                for case in obj.cases:
                    self.add_from_dict(case.inputs, next_levels)
            
            else:
                self.add_param(obj, levels)


    def add_param(self, obj, levels) -> None:
        if len(levels) == 0:
            key = '$' + obj.name
        else:
            key = '$' + '.'.join(levels) + '.' + obj.name
        if key not in self.params:
            self.params[key] = obj


    def get(self, query_key: str, ignore_path=False) -> Optional[ToolParameter]:
        # when we want to match full path
        if query_key in self.params:
            return self.params[query_key]

        # incase we dont care about path and just want final dot.
        # note that this is a backup, and still prioritises trying to find full path first
        if ignore_path == True:
            for key in list(self.params.keys()):
                nopath_key = key.rsplit('.')[-1]
                if nopath_key.endswith(query_key.lstrip('$')):
                    return self.params[key]

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

            if type(param) == SelectToolParameter:
                out = [opt[1] for opt in param.static_options]
            elif type(param) == BooleanToolParameter:
                out = [param.truevalue, param.falsevalue]
                out = [o for o in out if o != '']

        return out


