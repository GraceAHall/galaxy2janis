

from typing import Optional
from gx.gxtool.param.OutputParam import OutputParam

from gx.gxtool.param.ParamRegister import (
    ParamRegister,
    ExactSearchStrategy,
    LCASearchStrategy,
    FilepathSearchStrategy
)


class OutputParamRegister(ParamRegister):
    def __init__(self, params: list[OutputParam]):
        self.outputs: list[OutputParam] = []
        for param in params:
            self.add(param)

    def list(self) -> list[OutputParam]:
        return self.outputs
    
    def add(self, param: OutputParam) -> None:
        """adds a param to register. enforces unique param var names"""
        self.outputs.append(param)

    def get(self, query: str, strategy: str='exact') -> Optional[OutputParam]:
        """performs search using the specified search strategy"""
        strategy_map = {
            'exact': ExactSearchStrategy(),
            'lca': LCASearchStrategy(),
            'filepath': FilepathSearchStrategy(),
        }

        search_strategy = strategy_map[strategy]
        return search_strategy.search(query, self.outputs)



