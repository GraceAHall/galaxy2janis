

from typing import Optional

from xmltool.param.Param import Param 
from xmltool.param.ParamRegister import (
    ParamRegister,
    DefaultSearchStrategy,
    LCASearchStrategy,
    FilepathSearchStrategy
)


class OutputParamRegister(ParamRegister):
    def __init__(self, params: list[Param]):
        self.outputs: list[Param] = []
        for param in params:
            self.add(param)

    def list(self) -> list[Param]:
        return self.outputs
    
    def add(self, param: Param) -> None:
        """adds a param to register. enforces unique param var names"""
        self.outputs.append(param)

    def get(self, query: str, strategy: str='default') -> Optional[Param]:
        """performs search using the specified search strategy"""
        strategy_map = {
            'default': DefaultSearchStrategy(),
            'lca': LCASearchStrategy(),
            'filepath': FilepathSearchStrategy(),
        }

        search_strategy = strategy_map[strategy]
        return search_strategy.search(query, self.outputs)

















    # def create_output_from_text(self, text: str) -> None:
    #     """
    #     creates a new output using a dummy et.Element
    #     the new et.Element node is populated with some default details
    #     then is parsed as normal created the new output. 
    #     the output is added to our collection of outputs. 
    #     """
    #     # TODO 
    #     raise Exception('TODO: make galaxy ToolOutput not old Output')
    #     # create dummy node
    #     name = text.split('.', 1)[0]
    #     dummy_node = et.Element('data', attrib={'name': name, 'format': 'file', 'from_work_dir': text})
        
    #     # create and parse output
    #     new_output = ToolOutput(dummy_node)
    #     new_output.parse()

    #     # add to collection
    #     self.add([new_output])




