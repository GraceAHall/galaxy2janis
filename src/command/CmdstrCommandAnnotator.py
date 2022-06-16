
import runtime.logging.logging as logging

from xmltool.XMLToolDefinition import XMLToolDefinition
from command.Command import Command 
from command.cmdstr.CommandString import CommandString
from command.epath.ExecutionPath import ExecutionPath
from command.epath.ExecutionPathAnnotator import GreedyExecutionPathAnnotator


class CmdstrCommandAnnotator:

    def __init__(self, command: Command, xmltool: XMLToolDefinition, cmdstrs: list[CommandString]):
        self.command = command
        self.xmltool = xmltool
        self.cmdstrs = cmdstrs
        self.epath_count: int = 0

    def annotate(self) -> None:
        self.analyse_cmdstrs()
        self.cleanup()

    def analyse_cmdstrs(self) -> None:
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
            component.update_presence_array(self.epath_count)
            self.command.update(component)

    def cleanup(self) -> None:
        # just one thing to do
        self.update_components_presence_array()

    def update_components_presence_array(self) -> None:
        for component in self.command.list_inputs():
            component.update_presence_array(self.epath_count - 1, fill_false=True)
    