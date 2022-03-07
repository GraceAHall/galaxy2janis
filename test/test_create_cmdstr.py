



import unittest
from command.cmdstr.DynamicCommandString import DynamicCommandStringFactory
from command.tokens.TokenFactory import TokenFactory

from gxtool2janis import load_galaxy_manager, load_tool
from startup.settings import load_settings
from startup.ExeSettings import ToolExeSettings
from command.tokens.Tokens import TokenType


RAW_CMDSTR = "ln -sf 'gxvar_file_input' file_input &&  abricate file_input  --minid=80.0 --mincov=80.0 --db=resfinder > 'gxvar_report'"

STATEMENT0_STR = "ln -sf '$file_input' file_input"
STATEMENT1_STR = "abricate $file_input  --minid=80.0 --mincov=80.0 --db=resfinder > '$report'"

STATEMENT0_TOKENS = [
    [TokenType.RAW_STRING],
    [TokenType.RAW_STRING],
    [TokenType.GX_INPUT],
    [TokenType.RAW_STRING]
]
STATEMENT1_TOKENS = [
    [TokenType.RAW_STRING],
    [TokenType.GX_INPUT],
    [TokenType.KV_PAIR],
    [TokenType.KV_PAIR],
    [TokenType.KV_PAIR],
    [TokenType.LINUX_REDIRECT]
]


class TestCreateDynamicCommandString(unittest.TestCase):
    """
    tests whether CommandStatments are being correctly set up 
    """

    def setUp(self) -> None:
        argv = [
            "abricate.xml", "test/data/abricate", 
            "--outdir", "test/rubbish",
        ]
        esettings: ToolExeSettings = load_settings(argv)
        gxmanager = load_galaxy_manager(esettings)
        tool = load_tool(gxmanager)
        self.TokenFactory = TokenFactory(tool=tool)
        self.cmdstr_fac = DynamicCommandStringFactory(tool)

    def test_basic_overall_creation(self) -> None:
        cmdstr = self.cmdstr_fac.create('test', RAW_CMDSTR)
        self.assertEquals(len(cmdstr.statements), 2)
        self.assertEquals(cmdstr.statements[0].cmdline, STATEMENT0_STR)
        self.assertEquals(cmdstr.statements[1].cmdline, STATEMENT1_STR)

    def test_tokens(self) -> None:
        cmdstr = self.cmdstr_fac.create('test', RAW_CMDSTR)
        self.assertEquals(cmdstr.statements[0].tokens, STATEMENT0_TOKENS)
        self.assertEquals(cmdstr.statements[1].tokens, STATEMENT1_TOKENS)
        print()

    def test_stream_merges(self) -> None:
        print()
    
    def test_redirects(self) -> None:
        print()
    
    def test_tees(self) -> None:
        print()









