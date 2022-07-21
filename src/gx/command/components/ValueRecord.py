

from collections import defaultdict
from typing import Optional

from tokens import Token


class ValueRecord:
    def __init__(self):
        self.record: list[Token] = []

    def add(self, value: Token) -> None:
        self.record.append(value)

    @property
    def tokens(self) -> list[Token]:
        values = self.record
        values.sort(key=lambda x: x.text)
        return values
    
    @property
    def unique(self) -> list[str]:
        values = list(set([token.text for token in self.record]))
        values.sort()
        return values

    @property
    def env_var(self) -> Optional[str]:
        for token in self.record:
            if token.text.startswith('$'):
                return token.text
        return None

    @property
    def counts(self) -> defaultdict[str, int]:
        counts: defaultdict[str, int] = defaultdict(int) 
        for token in self.record:
            if token.text != '': # TODO how???
                counts[token.text] += 1
        return counts

    @property
    def most_common_value(self) -> Optional[str]:
        counts_dict = self.counts
        counts_list = list(counts_dict.items())
        counts_list.sort(key=lambda x: x[1], reverse=True)
        if len(counts_list) > 0:
            return counts_list[0][0]
        else:
            return None




