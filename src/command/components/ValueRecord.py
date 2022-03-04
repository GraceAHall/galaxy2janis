

from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any


class ValueRecord(ABC):
    @abstractmethod
    def add(self, obsval: Any) -> None:
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

    def get_most_common_value(self) -> str:
        counts_dict = self.get_counts()
        counts_list = list(counts_dict.items())
        counts_list.sort(key=lambda x: x[1], reverse=True)
        return counts_list[0][0]

    def is_int(self, the_string: str) -> bool:
        if the_string.isdigit():
            return True
        return False

    def is_float(self, the_string: str) -> bool:
        if not self.is_int(the_string):
            try:
                float(the_string)
                return True
            except ValueError:
                pass
        return False


class PositionalValueRecord(ValueRecord):
    def __init__(self):
        self.record: list[str] = []

    def add(self, obsval: str) -> None:
        self.record.append(obsval)

    def get_counts(self) -> defaultdict[str, int]:
        counts: defaultdict[str, int] = defaultdict(int) 
        for obsval in self.record:
            counts[obsval] += 1
        return counts

    def values_are_ints(self) -> bool:
        if all([self.is_int(x) for x in self.record]):
            return True
        return False
    
    def values_are_floats(self) -> bool:
        if all([self.is_float(x) for x in self.record]):
            return True
        return False

    def get_unique_values(self) -> list[str]:
        return list(set(self.record))


class OptionValueRecord(ValueRecord):
    def __init__(self):
        self.record: list[list[str]] = []

    def add(self, obsval: list[str]) -> None:
        self.record.append(obsval)

    def get_counts(self) -> defaultdict[str, int]:
        counts: defaultdict[str, int] = defaultdict(int) 
        for obsval_array in self.record:
            label = ' '.join(obsval_array)
            counts[label] += 1
        return counts

    def values_are_ints(self) -> bool:
        for obsval_array in self.record:
            if not all([self.is_int(x) for x in obsval_array]):
                return False
        return True
    
    def values_are_floats(self) -> bool:
        for obsval_array in self.record:
            if not all([self.is_float(x) for x in obsval_array]):
                return False
        return True

    def get_unique_values(self) -> list[str]:
        str_vals = [' '.join(obsval_array) for obsval_array in self.record]
        return list(set(str_vals))


