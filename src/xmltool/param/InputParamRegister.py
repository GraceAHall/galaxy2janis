


from typing import Optional

from xmltool.param.Param import Param 
from xmltool.param.ParamRegister import (
    ParamRegister,
    DefaultSearchStrategy,
    LCASearchStrategy
)

class InputParamRegister(ParamRegister):
    def __init__(self, params: list[Param]):
        self.inputs: list[Param] = []
        for param in params:
            self.add(param)

    def list(self) -> list[Param]:
        return list(self.inputs)
    
    def add(self, param: Param) -> None:
        self.inputs.append(param)
    
    def get(self, query: str, strategy: str='default') -> Optional[Param]:
        strategy_map = {
            'default': DefaultSearchStrategy(),
            'lca': LCASearchStrategy(),
        }
        search_strategy = strategy_map[strategy]
        return search_strategy.search(query, self.inputs)

