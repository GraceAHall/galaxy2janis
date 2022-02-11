

from typing import Optional
from command.alias.Alias import Alias


class AliasRegister:
    def __init__(self):
        self.aliases: dict[str, list[Alias]] = {}

    def add(self, source: str, dest: str, text: str) -> None:
        # check its not referencing itself
        if source != dest:
            alias = Alias(source, dest, text)
            
            # make sure a dict entry exists for the source      
            if alias.source not in self.aliases:
                self.aliases[alias.source] = []
            
            # make sure its not a duplicate
            if not self.exists(alias):
                self.aliases[alias.source].append(alias)

    def exists(self, query: Alias) -> bool:
        relevant_aliases = self.aliases[query.source]
        if any([query.dest == al.dest for al in relevant_aliases]):
            return True
        return False

    def get(self, querystr: str) -> Optional[list[Alias]]:
        if querystr in self.aliases:
            return self.aliases[querystr]

    def get_recursive(self, querystr: str) -> list[Alias]:
        out: list[Alias] = []
        if querystr in self.aliases:
            aliases = self.aliases[querystr]

            for alias in aliases:
                sub_aliases = self.get_recursive(alias.dest)
                if len(sub_aliases) > 0:
                    out += sub_aliases
                else:
                    out.append(alias)
        return out

    def get_sources(self) -> list[str]:
        return list(self.aliases.keys())
    
    def get_connections(self) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {}
        for source, aliases in self.aliases.items():
            out[source] = [al.dest for al in aliases]
        return out
