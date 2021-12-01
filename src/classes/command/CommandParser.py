

from typing import Optional, Any


from galaxy.tools import Tool as GalaxyTool
from classes.command.CommandString import CommandString
from classes.command.Command import Command
from classes.logging.Logger import Logger
from classes.tool.Tool import Tool

from classes.command.XMLCommandLoader import XMLCommandLoader
from classes.command.TestCommandLoader import TestCommandLoader
from classes.command.WorkflowStepCommandLoader import WorkflowStepCommandLoader



class CommandParser:
    """
    returns a Command()
    """
    def __init__(self, gxtool: GalaxyTool, tool: Tool, logger: Logger):
        self.gxtool = gxtool
        self.tool = tool
        self.logger = logger
        self.command = Command(self.tool.param_register, self.tool.out_register)
        

    def parse(self, workflow_step: Optional[dict[str, Any]]=None) -> Command:
        # self.update_command_from_janis_definition()  # NOTE FUTURE
        self.update_command_from_xml()
        self.update_command_from_tests()
        self.update_command_from_workflowstep(workflow_step)
      

    def update_command_from_xml(self) -> None:
        loader = XMLCommandLoader(self.gxtool, self.logger)
        cmd_txt = loader.load()
        cmd_str = CommandString(cmd_txt, self.tool, self.logger)
        self.command.update(cmd_str)

    
    def update_command_from_tests(self) -> None:
        loader = TestCommandLoader(self.gxtool, self.logger)
        for test in self.tool.tests:
            cmd_txt = loader.load(test)
            #cmd_str = CommandString(cmd_txt, self.tool, self.logger)
            #self.command.update(cmd_str)
    

    def update_command_from_workflowstep(self, workflow_step: dict[str, Any]) -> None:
        # temp testing
        workflow_step = {}
        if workflow_step is not None:
            loader = WorkflowStepCommandLoader(self.gxtool, self.logger)
            cmd_txt = loader.load(workflow_step)
            #cmd_str = CommandString(cmd_txt, self.tool, self.logger)
            #self.command.update(cmd_str)
    



