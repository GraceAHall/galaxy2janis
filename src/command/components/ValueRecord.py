

from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Optional

import utils.general_utils as utils 



class ValueRecord(ABC):
    def __init__(self):
        self.record: list[Any] = []

    @abstractmethod
    def add(self, value: Any) -> None:
        """adds an observed value to the record"""
        ...

    @abstractmethod
    def get_counts(self) -> defaultdict[str, int]:
        """returns how often a value was witnessed"""
        ...

    @abstractmethod
    def values_are_ints(self) -> bool:
        """returns true if all observed values are castable to int"""
        ...
    
    @abstractmethod
    def values_are_floats(self) -> bool:
        """returns true if all observed values are castable to float"""
        ...

    @abstractmethod
    def get_unique_values(self) -> list[str]:
        """returns all unique witnessed values"""
        ...

    def get_observed_env_var(self) -> Optional[str]:
        for obsval in self.record:
            if str(obsval).startswith('$'):
                return str(obsval)
        return None

    def get_most_common_value(self, no_env: bool=False) -> Optional[Any]:
        counts_dict = self.get_counts()
        counts_list = list(counts_dict.items())
        counts_list.sort(key=lambda x: x[1], reverse=True)
        if no_env:
            counts_list = [(val, count) for val, count in counts_list if not val.startswith('$')]

        if len(counts_list) > 0:
            return counts_list[0][0]
        else:
            return None


class PositionalValueRecord(ValueRecord):

    def add(self, value: Any) -> None:
        self.record.append(value)

    def get_counts(self) -> defaultdict[str, int]:
        counts: defaultdict[str, int] = defaultdict(int) 
        for obsval in self.record:
            if obsval != '':
                counts[obsval] += 1
        return counts

    def values_are_ints(self) -> bool:
        if all([utils.is_int(obsval) for obsval in self.record]):
            return True
        return False
    
    def values_are_floats(self) -> bool:
        if all([utils.is_float(obsval) for obsval in self.record]):
            return True
        return False

    def get_unique_values(self) -> list[str]:
        values = list(set([obsval for obsval in self.record]))
        values.sort()
        return values




# should be cmdstr_count, value
class OptionValueRecord(ValueRecord):

    def add(self, value: list[str]) -> None:
        self.record.append(value)

    def get_counts(self) -> defaultdict[str, int]:
        counts: defaultdict[str, int] = defaultdict(int) 
        for obsval in self.record:
            if len(obsval) > 0:
                label = ' '.join(obsval)
                counts[label] += 1
        return counts

    def values_are_ints(self) -> bool:
        for obsval in self.record:
            if not all([utils.is_int(x) for x in obsval]):
                return False
        return True
    
    def values_are_floats(self) -> bool:
        for obsval in self.record:
            if not all([utils.is_float(x) for x in obsval]):
                return False
        return True

    def get_unique_values(self) -> list[str]:
        str_vals = [' '.join(obsval) for obsval in self.record]
        str_vals = list(set(str_vals))
        str_vals.sort()
        return str_vals


