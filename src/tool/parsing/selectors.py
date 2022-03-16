



from abc import ABC
from dataclasses import dataclass
from enum import Enum, auto
from galaxy.tool_util.parser.output_objects import ToolOutput as GxOutput


# this module is kinda a factory but I dont feel like a factor class is right

# helper classes 
class SelectorType(Enum):
    INPUT_SELECTOR = auto()
    WILDCARD_SELECTOR = auto()
    STRING_FORMATTER = auto()


@dataclass
class Selector:
    stype: SelectorType
    contents: str


class Strategy(ABC):
    def fetch(self, gxout: GxOutput) -> Selector:
        """creates Selector for this galaxy output"""
        ...

class FromWorkDirStrategy(Strategy):
    def fetch(self, gxout: GxOutput) -> Selector:
        return Selector(
            SelectorType.WILDCARD_SELECTOR, 
            str(gxout.from_work_dir)
        )

class CollectorStrategy(Strategy):
    def fetch(self, gxout: GxOutput) -> Selector:
        collector = gxout.dataset_collector_descriptions[0]
        return Selector(
            SelectorType.WILDCARD_SELECTOR, 
            f'{collector.directory}/{collector.pattern}'
        )

class FallbackStrategy(Strategy):
    def fetch(self, gxout: GxOutput) -> Selector:
        return Selector(
            SelectorType.INPUT_SELECTOR, 
            str(gxout.name)
        )


def fetch_selector(gxout: GxOutput) -> Selector:
    strategy: Strategy = select_fetcher(gxout)
    return strategy.fetch(gxout)

def select_fetcher(gxout: GxOutput) -> Strategy:
    if has_fromworkdir(gxout):
        return FromWorkDirStrategy()
    elif has_dataset_collector(gxout):
        return CollectorStrategy()
    else:
        return FallbackStrategy()

def has_fromworkdir(gxout: GxOutput) -> bool:
    if gxout.output_type == 'data':
        if hasattr(gxout, 'from_work_dir') and gxout.from_work_dir:
            return True
    return False

def has_dataset_collector(gxout: GxOutput) -> bool:
    if hasattr(gxout, 'dynamic_structure') and gxout.dynamic_structure:
        if hasattr(gxout, 'dataset_collector_descriptions'):
            return True
    return False
    
        