

from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Optional



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

    @property
    @abstractmethod
    def unique_values(self) -> list[str]:
        """returns all unique witnessed values"""
        ...

    def get_observed_env_var(self) -> Optional[str]:
        for obsval in self.record:
            if str(obsval).startswith('$'):
                return str(obsval)
        return None

    def get_most_common_value(self) -> Optional[Any]:
        counts_dict = self.get_counts()
        counts_list = list(counts_dict.items())
        counts_list.sort(key=lambda x: x[1], reverse=True)
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

    @property
    def unique_values(self) -> list[str]:
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

    @property
    def unique_values(self) -> list[str]:
        str_vals = [' '.join(obsval) for obsval in self.record]
        str_vals = list(set(str_vals))
        str_vals.sort()
        return str_vals


