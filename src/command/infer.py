

from command.components.CommandComponent import CommandComponent
from command.components.inputs.Flag import Flag
from command.components.inputs.Option import Option
from command.tokens.Tokens import Token
from galaxy_interaction import GalaxyManager
from xmltool.param.InputParam import BoolParam, SelectParam
from xmltool.param.Param import Param
from xmltool.tool_definition import XMLToolDefinition

from command.cmdstr.CommandString import CommandString
from command.cmdstr.CommandStringFactory import CommandStringFactory
from command.Command import Command
from command.CommandFactory import CommandFactory
from command.components.inputs import spawn_component 



# names are really misleading here. 
def infer_command(gxmanager: GalaxyManager, xmltool: XMLToolDefinition) -> Command:
    ci = CommandInferer(gxmanager, xmltool)
    return ci.infer()


# class just exists to avoid passing variables
class CommandInferer:
    command: Command

    def __init__(self, gxmanager: GalaxyManager, xmltool: XMLToolDefinition) -> None:
        self.gxmanager = gxmanager
        self.xmltool = xmltool
        self.cmdstrs: list[CommandString] = []
        self.cmdstr_factory = CommandStringFactory(self.xmltool)
        self.command_factory = CommandFactory(self.xmltool)
    
    def infer(self) -> Command:
        """infer a Command using cmdstrs and gxparams with arguments field"""
        self.gen_cmd_strings() 
        self.gen_command() 
        self.update_command_with_gx_argument_params() 
        return self.command

    def gen_cmd_strings(self) -> None:
        # create command strings (from evaluated tests, simplified xml <command>)
        self.gen_test_cmdstrs()
        self.gen_xml_cmdstr()
        
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
        # parse command strings to infer components
        self.command = self.command_factory.create(self.cmdstrs)
    
    def update_command_with_gx_argument_params(self) -> None:
        # add any gxparams which hint they are components (or update the component)
        for gxparam in self.xmltool.list_inputs():
            if self.should_update_command_components(gxparam):
                self.update_command_components(gxparam)
    
    def should_update_command_components(self, gxparam: Param) -> bool:
        # check the gxparam has an argument, and the argument isn't weirdly written
        banned_argument_chars = [' ', '/', '\\']
        if gxparam.argument: # type: ignore
            if any([char in gxparam.argument for char in banned_argument_chars]):
                return False
                # check whether the argument is already known as a prefix 
                prefix_components: list[Flag | Option] = []
                prefix_components += self.command.get_flags()
                prefix_components += self.command.get_options()
                for component in prefix_components:
                    if gxparam.argument == component.prefix: # type: ignore
                        return False
            else:
                return True
        return False

    def update_command_components(self, gxparam: Param) -> None:
        """
        gxparam definitely has 'argument' field
        the below are assumptions - galaxy XML can be written any way you want
        """
        # check the argument wasn't written weirdly
        assert(gxparam.argument) # type: ignore
        match gxparam:
            case BoolParam():
                component = spawn_component(
                    comp_type='flag', 
                    ctext=gxparam.argument, 
                    ntexts=[], 
                    epath_id=-1
                )
                component.gxparam = gxparam
                self.command.update(component)
            case SelectParam():
                for opt in gxparam.options:
                    component = spawn_component(
                        comp_type='option', 
                        ctext=gxparam.argument, 
                        ntexts=[opt.value], 
                        epath_id=-1
                    )
                    component.gxparam = gxparam
                    self.command.update(component)
            case _:
                component = spawn_component(
                    comp_type='option', 
                    ctext=gxparam.argument, 
                    ntexts=[], 
                    epath_id=-1
                )
                component.gxparam = gxparam
                self.command.update(component)
    

    def print_cmdstrs(self) -> None:
        test_cmdstrs = [x for x in self.cmdstrs if x.source == 'test']
        xml_cmdstrs = [x for x in self.cmdstrs if x.source == 'xml']

        print('\nCommand strings being fed for inference ------------------------')
        print('\nTests:\n')
        for cmdstr in test_cmdstrs:
            cmdstr.main.print_execution_paths()
        print('\n\nXml:\n')
        for cmdstr in xml_cmdstrs:
            cmdstr.main.print_execution_paths()
        print()



