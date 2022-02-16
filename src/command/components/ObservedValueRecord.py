

from collections import defaultdict
from dataclasses import dataclass
from typing import Optional



@dataclass
class ObservedValue:
    value: str
    cmdstr_index: int 

class ObservedValueRecord:
    def __init__(self):
        self.record: list[ObservedValue] = []

    def update(self, obsval: ObservedValue) -> None:
        self.record.append(obsval)

    def get_counts(self) -> defaultdict[str, int]:
        counts: defaultdict[str, int] = defaultdict(int) 
        for obsval in self.record:
            counts[obsval.value] += 1
        return counts

    def get_cmdstr_index_value(self, cmdstr_index: int) -> Optional[str]:
        for obsval in self.record:
            if obsval.cmdstr_index == cmdstr_index:
                return obsval.value
        return None

    def get_most_common_value(self) -> Optional[str]:
        counts_dict = self.get_counts()
        counts_list = list(counts_dict.items())
        counts_list.sort(key=lambda x: x[1], reverse=True)
        return counts_list[0][0]

