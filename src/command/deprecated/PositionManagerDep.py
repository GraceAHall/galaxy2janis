





from dataclasses import dataclass
from enum import Enum, auto

from command.components.CommandComponent import CommandComponent


class CmdStrStage(Enum):
    PRE_OPTIONS = auto()
    IN_OPTIONS = auto()
    POST_OPTIONS = auto()

enum_str_map = {
    CmdStrStage.PRE_OPTIONS: 'pre_options',
    CmdStrStage.IN_OPTIONS: 'in_options',
    CmdStrStage.POST_OPTIONS: 'post_options',
}


@dataclass
class PositionManager:
    """
    manages our position within the epath being iterated through
    """
    stage: CmdStrStage = CmdStrStage.PRE_OPTIONS
    options_encountered: bool = False

    def reset(self) -> None:
        self.stage = CmdStrStage.PRE_OPTIONS
        self.options_encountered = False

    def update(self, comp_type: str) -> None:
        self.update_options_encountered(comp_type)
        self.update_stage(comp_type)
        
    def update_options_encountered(self, comp_type: str) -> None:
        if comp_type in ['flag', 'option']:
            self.options_encountered = True

    def update_stage(self, comp_type: str) -> None:
        if self.stage == CmdStrStage.PRE_OPTIONS and self.options_encountered:
            self.increment_stage()
        if self.stage == CmdStrStage.IN_OPTIONS and comp_type == 'positional':
            self.increment_stage()

    def increment_stage(self) -> None:
        match self.stage:
            case CmdStrStage.PRE_OPTIONS:
                self.stage = CmdStrStage.IN_OPTIONS
            case CmdStrStage.IN_OPTIONS:
                self.stage = CmdStrStage.POST_OPTIONS
            case _:
                pass

    def mark_component_stage(self, component: CommandComponent) -> None:
        component.stage = enum_str_map[self.stage]