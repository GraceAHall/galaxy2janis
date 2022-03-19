

from galaxy_interaction import GalaxyManager
from xmltool.tool_definition import XMLToolDefinition

from command.cmdstr.DynamicCommandString import DynamicCommandString
from command.cmdstr.DynamicCommandStringFactory import DynamicCommandStringFactory
from command.Command import Command
from command.CommandFactory import CommandFactory


def infer_command_components(gxmanager: GalaxyManager, xmltool: XMLToolDefinition) -> Command:
    ci = ComponentInferer(gxmanager, xmltool)
    ci.gen_cmd_strings()
    ci.gen_command()
    return ci.command


# class just exists to avoid passing variables
class ComponentInferer:
    command: Command
    cmdstrs: list[DynamicCommandString] = []

    def __init__(self, gxmanager: GalaxyManager, xmltool: XMLToolDefinition) -> None:
        self.gxmanager = gxmanager
        self.xmltool = xmltool
        self.cmdstr_factory = DynamicCommandStringFactory(self.xmltool)

    def gen_cmd_strings(self) -> None:
        self.gen_test_cmdstrs()
        self.gen_xml_cmdstr()
        #self.gen_workflow_cmdstr()
        
    def gen_test_cmdstrs(self) -> None:
        for test_str in self.gxmanager.get_test_cmdstrs(self.xmltool):
            cmdstr = self.cmdstr_factory.create('test', test_str)
            self.cmdstrs.append(cmdstr)

    def gen_xml_cmdstr(self) -> None:
        xml_str = self.gxmanager.get_xml_cmdstr(self.xmltool)
        cmdstr = self.cmdstr_factory.create('xml', xml_str)
        self.cmdstrs.append(cmdstr)

    def gen_workflow_cmdstr(self) -> str:
        raise NotImplementedError
   
    def gen_command(self) -> None:
        factory = CommandFactory(self.xmltool)
        self.command = factory.create(self.cmdstrs)

    def print_cmdstrs(self) -> None:
        test_cmdstrs = [x for x in self.cmdstrs if x.source == 'test']
        xml_cmdstrs = [x for x in self.cmdstrs if x.source == 'xml']

        print('\nCommand strings being fed for inference ------------------------')
        print('\nTests:\n')
        for cmdstr in test_cmdstrs:
            cmdstr.tool_statement.print_execution_paths()
        print('\n\nXml:\n')
        for cmdstr in xml_cmdstrs:
            cmdstr.tool_statement.print_execution_paths()
        print()



