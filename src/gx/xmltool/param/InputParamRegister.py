


from typing import Optional

from gx.xmltool.param.Param import Param 
from gx.xmltool.param.ParamRegister import (
    ParamRegister,
    ExactSearchStrategy,
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
    
    def get(self, query: str, strategy: str='exact') -> Optional[Param]:
        strategy_map = {
            'exact': ExactSearchStrategy(),
            'lca': LCASearchStrategy(),
        }
        search_strategy = strategy_map[strategy]
        return search_strategy.search(query, self.inputs)

