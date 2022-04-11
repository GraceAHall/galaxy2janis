

from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass

from xmltool.param.Param import Param 


class ParamRegister(ABC):
    @abstractmethod
    def list(self) -> list[Param]:
        ...
    
    @abstractmethod
    def add(self, param: Param) -> None:
        ...
    
    @abstractmethod
    def get(self, query: str, strategy: str='default') -> Optional[Param]:
        ...


class SearchStrategy(ABC):    
    @abstractmethod
    def search(self, query: str, params: list[Param]) -> Optional[Param]:
        """searches for a param using some concrete strategy"""
        ...

class DefaultSearchStrategy(SearchStrategy):
    def search(self, query: str, params: list[Param]) -> Optional[Param]:
        """searches for a param using param name"""
        for param in params:
            if param.name == query:
                return param
        return None

@dataclass
class LCAParam:
    split_name: list[str]
    param: Param

class LCASearchStrategy(SearchStrategy):
    def search(self, query: str, params: list[Param]) -> Optional[Param]:
        """searches for a param using LCA"""
        split_query = query.split('.')
        remaining_params = self.init_datastructure(params)

        for i in range(1, len(split_query) + 1):
            remaining_params = [p for p in remaining_params if len(p.split_name) >= i]
            remaining_params = [p for p in remaining_params if p.split_name[-i] == split_query[-i]]

        if len(remaining_params) > 0:
            # return shortest param name which matches the query
            remaining_params.sort(key=lambda x: len(x.split_name))
            return remaining_params[0].param

    def init_datastructure(self, params: list[Param]):
        return [LCAParam(param.name.split('.'), param) for param in params]
        

class FilepathSearchStrategy(SearchStrategy):
    def search(self, query: str, params: list[Param]) -> Optional[Param]:
        """
        searches for a param by matching the specified 
        from_work_dir path to a given filepath
        """
        raise NotImplementedError
        # for param in params.values():
        #     if hasattr(param, 'from_work_dir') and param.from_work_dir == query:
        #         return param


    

