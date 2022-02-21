

from collections import defaultdict
from typing import Optional


class ObservedValueRecord:
    def __init__(self):
        self.record: list[str] = []

    def add(self, obsval: str) -> None:
        self.record.append(obsval)

    def get_counts(self) -> defaultdict[str, int]:
        counts: defaultdict[str, int] = defaultdict(int) 
        for obsval in self.record:
            counts[obsval] += 1
        return counts

    def get_most_common_value(self) -> Optional[str]:
        counts_dict = self.get_counts()
        counts_list = list(counts_dict.items())
        counts_list.sort(key=lambda x: x[1], reverse=True)
        return counts_list[0][0]

    def values_are_ints(self) -> bool:
        if all([self.is_int(x) for x in self.record]):
            return True
        return False
    
    def values_are_floats(self) -> bool:
        if all([self.is_float(x) for x in self.record]):
            return True
        return False

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

