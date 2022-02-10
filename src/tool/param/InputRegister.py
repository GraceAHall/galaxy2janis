


from typing import Any, Optional

from tool.param.Param import Param 
from tool.param.ParamRegister import (
    ParamRegister,
    DefaultSearchStrategy,
    LCASearchStrategy
)

class InputRegister(ParamRegister):
    def __init__(self, params: list[Param]):
        self.inputs: dict[str, Param] = dict()
        for param in params:
            self.add(param)

    def list(self) -> list[Param]:
        return list(self.inputs.values())
    
    def add(self, param: Param) -> None:
        if param.name not in self.inputs:
            self.inputs[param.name] = param
    
    def get(self, query: str, strategy: str='default') -> Optional[Param]:
        strategy_map = {
            'default': DefaultSearchStrategy(),
            'lca': LCASearchStrategy(),
        }
        search_strategy = strategy_map[strategy]
        return search_strategy.search(query, self.inputs)

    def to_dict(self) -> dict[str, Any]:
        param_dict: dict[str, Any] = {}
        for varname, param in self.inputs.items():
            node = param_dict
            varpath = varname.split('.')
            for i, text in enumerate(varpath):
                if text not in node:
                    if i == len(varpath) - 1:
                        # terminal path, add param to node
                        node[text] = param.get_default()
                        break
                    else:
                        # create new node for section
                        node[text] = {}
                node = node[text]
        return param_dict


    
    """
    def to_json(self) -> dict[str, Any]:
        param_dict = self._get_param_dict()
        param_dict = self._jsonify_param_dict(param_dict)
        return param_dict

    def _get_param_dict(self) -> dict[str, Any]:
        param_dict: dict[str, Any] = {}
        for varname, param in self.inputs.items():
            node = param_dict
            varpath = varname.split('.')
            for i, text in enumerate(varpath):
                if text not in node:
                    if i == len(varpath) - 1:
                        # terminal path, add param to node
                        node[text] = param.get_default()
                        break
                    else:
                        # create new node for section
                        node[text] = {}
                node = node[text]
        return param_dict

    def _jsonify_param_dict(self, param_dict: dict[str, Any]) -> dict[str, Any]:
        for key, val in param_dict.items():
            if type(val) == dict:
                param_dict[key] = json.dumps(val)  
        return param_dict
    """


