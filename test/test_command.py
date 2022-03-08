



from typing import Any
import unittest

# setup imports
from data.tool_args import passing_tools
from startup.settings import load_tool_settings
from startup.ExeSettings import ToolExeSettings
from galaxy_interaction import load_manager, GalaxyManager
from tool.load import load_tool, GalaxyToolDefinition

from command.infer import infer_command


class TestCommandInference(unittest.TestCase):
    """tests whether a Command() is correctly generated"""

    def setUp(self) -> None:
        args = passing_tools['abricate']
        esettings: ToolExeSettings = load_tool_settings(args) 
        gxmanager: GalaxyManager = load_manager(esettings)
        self.tool: GalaxyToolDefinition = load_tool(gxmanager)
        self.command = infer_command(gxmanager, self.tool)

    def test_command_positionals(self) -> None:
        cmd = self.command
        self.assertEquals(len(cmd.positionals), 2)

        posit1 = cmd.positionals[1]
        self.assertEquals(posit1.get_default_value(), 'abricate')
        self.assertEquals(posit1.value_record.get_counts()['abricate'], 17)
        self.assertEquals(posit1.is_optional(), False)
        
        posit2 = cmd.positionals[2]
        self.assertEquals(posit2.get_default_value(), '$sample_name')
        self.assertEquals(posit2.is_optional(), False)
    
    def test_command_flags(self) -> None:
        cmd = self.command
        self.assertEquals(len(cmd.flags), 1)

        target_flags = ['--noheader']
        for prefix in target_flags:
            flag = cmd.flags[prefix]
            self.assertIsNotNone(flag.gxvar)
            self.assertEquals(flag.prefix, prefix)
            self.assertEquals(flag.is_optional(), True)
    
    def test_command_options(self) -> None:
        cmd = self.command
        self.assertEquals(len(cmd.options), 3)
        target_options = {
            '--db': {
                'delim': '=',
                'default': 'resfinder',
                'has_gxvar': True,
                'is_optional': False
            },
            '--minid': {
                'delim': '=',
                'default': '80',
                'has_gxvar': True,
                'is_optional': False
            },
            '--mincov': {
                'delim': '=',
                'default': '80',
                'has_gxvar': True,
                'is_optional': False
            }
        }
        for prefix, details in target_options.items():
            option = cmd.options[prefix]
            self.assertEquals(option.delim, details['delim'])
            self.assertEquals(option.get_default_value(), details['default'])
            self.assertEquals(option.gxvar is not None, details['has_gxvar'])
            self.assertEquals(option.is_optional(), details['is_optional'])

    def test_command_stdout(self) -> None:
        redirect: Any = self.command.redirect
        self.assertIsNotNone(redirect)
        self.assertIsNotNone(redirect.gxvar)
        self.assertEquals(redirect.file.text, '$report')




# RAW_CMDSTR = "ln -sf 'gxvar_file_input' file_input &&  abricate file_input  --minid=80.0 --mincov=80.0 --db=resfinder > 'gxvar_report'"

# STATEMENT0_STR = "ln -sf '$file_input' file_input"
# STATEMENT1_STR = "abricate $file_input  --minid=80.0 --mincov=80.0 --db=resfinder > '$report'"


# STATEMENT0_TOKENS = [
#     [TokenType.RAW_STRING],
#     [TokenType.RAW_STRING],
#     [TokenType.GX_INPUT],
#     [TokenType.RAW_STRING]
# ]
# STATEMENT1_TOKENS = [
#     [TokenType.RAW_STRING],
#     [TokenType.GX_INPUT],
#     [TokenType.KV_PAIR],
#     [TokenType.KV_PAIR],
#     [TokenType.KV_PAIR],
#     [TokenType.LINUX_REDIRECT]
# ]


# class TestCreateDynamicCommandString(unittest.TestCase):
#     """
#     tests whether CommandStatments are being correctly set up 
#     """
#     def setUp(self) -> None:
#         args = passing_tools['abricate']
#         esettings: ToolExeSettings = load_tool_settings(args) 
#         gxmanager: GalaxyManager = load_manager(esettings)
#         tool: GalaxyToolDefinition = load_tool(gxmanager)
#         self.factory = DynamicCommandStringFactory(tool)

#     def test_basic_overall_creation(self) -> None:
#         cmdstr = self.factory.create('test', RAW_CMDSTR)
#         self.assertEquals(len(cmdstr.statements), 2)
#         self.assertEquals(cmdstr.statements[0].cmdline, STATEMENT0_STR)
#         self.assertEquals(cmdstr.statements[1].cmdline, STATEMENT1_STR)

#     def test_tokens(self) -> None:
#         cmdstr = self.factory.create('test', RAW_CMDSTR)
#         self.assertEquals(cmdstr.statements[0].tokens, STATEMENT0_TOKENS)
#         self.assertEquals(cmdstr.statements[1].tokens, STATEMENT1_TOKENS)

#     def test_stream_merges(self) -> None:
#         print()
    
#     def test_redirects(self) -> None:
#         print()
    
#     def test_tees(self) -> None:
#         print()









