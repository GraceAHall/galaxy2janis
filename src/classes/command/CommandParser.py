

from typing import Optional, Any


from galaxy.tools import Tool as GalaxyTool
from classes.tool.Tool import Tool
from classes.templating.MockClasses import MockApp
from classes.command.CommandString import CommandString
from classes.command.Command import Command
from classes.command.XMLCommandLoader import XMLCommandLoader
from classes.command.TestCommandLoader import TestCommandLoader
from classes.command.WorkflowStepCommandLoader import WorkflowStepCommandLoader
from classes.logging.Logger import Logger


class CommandParser:
    """
    returns a Command()
    """
    def __init__(self, app: MockApp, gxtool: GalaxyTool, tool: Tool, logger: Logger):
        self.app = app
        self.gxtool = gxtool
        self.tool = tool
        self.logger = logger
        self.command = Command(self.tool.param_register, self.tool.out_register)
        

    def parse(self, workflow: Optional[dict[str, Any]]=None, workflow_step: int=0) -> Command:
        # self.update_command_from_janis_definition()  # NOTE FUTURE
        self.update_command_from_tests()
        #self.update_command_from_workflowstep(workflow, workflow_step)
        self.update_command_from_xml()
        self.command.set_component_positions()
        return self.command
      

    def update_command_from_tests(self) -> None:
        loader = TestCommandLoader(self.app, self.gxtool, self.tool, self.logger)
        for i, test in enumerate(self.tool.tests):
            cmd_txt = loader.load(test)
            if cmd_txt is not None:
                print(cmd_txt)
                cmd_str = CommandString(cmd_txt, self.tool, self.logger)
                #print('\nTEST\n', cmd_str)
                self.command.update(cmd_str, source='test')
                print(f'\nTEST {i}\n', self.command)
    

    def update_command_from_workflowstep(self, workflow: Optional[dict[str, Any]]=None, workflow_step: int=0) -> None:
        loader = WorkflowStepCommandLoader(self.app, self.gxtool, self.tool, self.logger)
        if workflow_step is not None:
            cmd_txt = loader.load(workflow, workflow_step)
            cmd_str = CommandString(cmd_txt, self.tool, self.logger)
            #print('\nWORKFLOW STEP\n', cmd_str)
            self.command.update(cmd_str, source='workflowstep')
            print(f'\nWORKFLOW STEP\n', self.command)
    

    def update_command_from_xml(self) -> None:
        loader = XMLCommandLoader(self.gxtool, self.logger)
        cmd_txt = loader.load()
        cmd_str = CommandString(cmd_txt, self.tool, self.logger)
        #print('\nXML\n', cmd_str)
        self.command.update(cmd_str, source='xml')
        print(f'\nXML\n', self.command)


