


from typing import Optional, Tuple, Any
from copy import deepcopy
import json

from galaxy.tools.parameters.basic import (
    ToolParameter,
    BooleanToolParameter,
    SelectToolParameter
)


class ParamRegister:
    def __init__(self, inputs: dict) -> None:
        self.params: dict[str, ToolParameter] = {}
        self.update(inputs, [])
        print()


    def to_job_dict(self, value_overrides: Optional[dict]=None) -> dict:
        out_dict = {}

        for varname, param in self.params.items():
            varpath = varname.split('.')
            node = out_dict
            
            for i, text in enumerate(varpath):
                if text not in node:
                    if i == len(varpath) - 1:
                        # terminal path, add param to node
                        if value_overrides is not None and varname in value_overrides:
                            node[text] = value_overrides[varname]
                        else:
                            node[text] = self.get_param_default_value(param)
                        break
                    else:
                        # create new node for section
                        node[text] = {}

                node = node[text]    

        for key, val in out_dict.items():
            if type(val) == dict:
                out_dict[key] = json.dumps(val)            
        
        return out_dict


    def get_param_default_value(self, param: ToolParameter) -> Any:
        # param has value
        if hasattr(param, 'value'):
            return param.value
        
        # selected option
        elif param.type == 'select':
            for opt in param.static_options:
                if opt[2] == True:
                    return opt[1]
            return None

        # bool state
        elif param.type == 'boolean':
            return param.checked
        
        # just in case none of the above find anything
        return None
        

    def update(self, inputs: dict, levels: list[str]) -> None:
        for label, obj in inputs.items():
            if hasattr(obj, 'inputs'):
                next_levels = deepcopy(levels)
                next_levels.append(obj.name)
                self.update(obj.inputs, next_levels)

            elif hasattr(obj, 'cases'):
                next_levels = deepcopy(levels)
                next_levels.append(obj.name)
                self.add(obj.test_param, next_levels)
                for case in obj.cases:
                    self.update(case.inputs, next_levels)
            
            else:
                self.add(obj, levels)


    def add(self, obj, levels) -> None:
        if len(levels) == 0:
            key = obj.name
        else:
            key = '.'.join(levels) + '.' + obj.name
        if key not in self.params:
            self.params[key] = obj


    def get(self, query_key: str, allow_lca=False) -> Tuple[Optional[str], Optional[ToolParameter]]:
        # quick check if the full key is present
        if query_key in self.params:
            return (query_key, self.params[query_key])

        # otherwise, get the param with best match (LCA)
        if allow_lca:
            return self.get_lca(query_key)

        return (None, None)


    def get_lca(self, query_key: str) -> Tuple[Optional[str], Optional[ToolParameter]]:
        """
        returns the parameter with best similarity to the query key
        uses a lowest-common-ancestor approach, where the param path 
        is matched iteratively, starting at the final label, and working
        back. 
        eg params: [
            $t,
            $adv.alignment.t,
            $adv.alignment.v,
            $adv.alignment.c,
        ]
        if query_key == $adv.alignment.t, then $adv.alignment.t will be returned.
        it will have a score of 3, whereas just $t will have a score of 1.

        if query_key == $t, then $t will be returned.
        both $t and $adv.alignment.t will have score=1, but $t appeared first in xml 
        (so is first in self.params) and will be at the top of the sorted score list. 
        """
        query_path = query_key.split('.')
        param_scores: list[Tuple[int, str, ToolParameter]] = []

        for param_var, param in self.params.items():
            var_path = param_var.split('.')
            score = 0
            for i in range(1, len(query_path) + 1):
                if var_path[-i] == query_path[-i]:
                    score += 1
                else:
                    break
            param_scores.append((score, param_var, param))
        
        # params are ordered by the place in xml
        # python sort is stable so if there are multiple equally
        # good matches (ie non unique), the param which first appears in 
        # the xml is returned. this is consistent with planemo behaviour. 
        param_scores.sort(key=lambda x: x[0], reverse=True)

        if param_scores[0][0] >= 1:
            return param_scores[0][1,2]
        return (None, None)



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


