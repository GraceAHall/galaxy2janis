

from command.Command import Command 

from xmltool.tool_definition import XMLToolDefinition
from command.cmdstr.CommandString import CommandString

from command.epath.ExecutionPath import ExecutionPath
from command.epath.GreedyEPathAnnotator import GreedyEPathAnnotator


class CmdstrCommandAnnotator:

    def __init__(self, command: Command, xmltool: XMLToolDefinition, cmdstrs: list[CommandString]):
        self.command = command
        self.xmltool = xmltool
        self.cmdstrs = cmdstrs

        self.epath_count: int = 0

    def annotate(self) -> None:
        self.analyse_cmdstrs(source='xml')
        self.analyse_cmdstrs(source='test')
        self.cleanup()

    def analyse_cmdstrs(self, source: str) -> None:
        active_cmdstrs = [c for c in self.cmdstrs if c.source == source]
        for cmdstr in active_cmdstrs:
            for epath in cmdstr.main.get_execution_paths():
                print(epath)
                self.extract_components(epath)

    def extract_components(self, epath: ExecutionPath) -> None:
        epath.id = self.epath_count
        epath = self.assign_epath_components(epath)
        self.update_command(epath)
        self.epath_count += 1
    
    def assign_epath_components(self, epath: ExecutionPath) -> ExecutionPath:
        annotator = GreedyEPathAnnotator(epath, self.xmltool, self.command)
        return annotator.annotate_epath()

    def update_command(self, epath: ExecutionPath) -> None:
        """
        updates command components using an annotated epath
        """
        self.update_command_components(epath)
        self.update_redirects(epath)

    def update_command_components(self, epath: ExecutionPath) -> None:
        for component in epath.get_components():
            component.update_presence_array(self.epath_count)
            self.command.update(component)

    def update_redirects(self, epath: ExecutionPath) -> None:
        if epath.redirect and epath.redirect.file_token.gxparam:
            self.command.update(epath.redirect)
   
    def cleanup(self) -> None:
        # just one thing to do
        self.update_components_presence_array()

    def update_components_presence_array(self) -> None:
        for component in self.command.list_inputs():
            component.update_presence_array(self.epath_count - 1, fill_false=True)
    