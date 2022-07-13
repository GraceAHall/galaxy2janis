
import logs.logging as logging

from gx.gxtool.XMLToolDefinition import XMLToolDefinition

from .Command import Command 
from .cmdstr.CommandString import CommandString

from shellparser.epath.ExecutionPath import ExecutionPath
from shellparser.epath.ExecutionPathAnnotator import GreedyExecutionPathAnnotator


class CmdstrCommandAnnotator:

    def __init__(self, command: Command, xmltool: XMLToolDefinition, cmdstrs: list[CommandString]):
        self.command = command
        self.xmltool = xmltool
        self.cmdstrs = cmdstrs
        self.epath_count: int = 0

    def annotate(self) -> None:
        for cmdstr in self.cmdstrs:
            for epath in cmdstr.main.get_execution_paths():
                logging.runtime_data(str(epath))
                self.extract_components(epath)

    def extract_components(self, epath: ExecutionPath) -> None:
        epath.id = self.epath_count
        epath = self.assign_epath_components(epath)
        self.update_command(epath)
        self.epath_count += 1
    
    def assign_epath_components(self, epath: ExecutionPath) -> ExecutionPath:
        annotator = GreedyExecutionPathAnnotator(epath, self.xmltool, self.command)
        return annotator.annotate()

    def update_command(self, epath: ExecutionPath) -> None:
        for component in epath.get_components():
            self.command.update(component)
