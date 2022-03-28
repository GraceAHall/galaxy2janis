



from dataclasses import dataclass, field
from typing import Any, Tuple



# DEPRECATED
@dataclass
class InputValueRegister:
    register: dict[str, Any] = field(default_factory=dict)

    def add(self, name: str, value: Any) -> None:
        self.register[name] = value

    def list(self) -> list[Tuple[str, Any]]:
        return list(self.register.items())

    def get_value(self, query: str) -> Any:
        if query in self.register:
            return self.register[query]
        raise RuntimeError()



