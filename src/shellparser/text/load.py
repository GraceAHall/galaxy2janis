

from gx.interaction import GalaxyInteractor
from gx.xmltool.load import load_xmltool
from shellparser.text.simplification import ( 
    simplify_xml, 
    simplify_xml_cheetah_eval, 
    simplify_test 
)

def load_xml_command() -> str:
    gxmanager = GalaxyInteractor()
    xmltool = load_xmltool()
    cmdstr = gxmanager.get_xml_cmdstr(xmltool)
    cmdstr = simplify_xml(cmdstr)
    return cmdstr

def load_xml_command_cheetah_eval() -> str:
    gxmanager = GalaxyInteractor()
    xmltool = load_xmltool()
    cmdstr = gxmanager.get_xml_cmdstr(xmltool)
    cmdstr = simplify_xml_cheetah_eval(cmdstr)
    return cmdstr
    
def load_test_commands() -> list[str]:
    cmdstrs: list[str] = []
    gxmanager = GalaxyInteractor()
    xmltool = load_xmltool()
    for teststr in gxmanager.get_test_cmdstrs(xmltool):
        teststr = simplify_test(teststr)
        cmdstrs.append(teststr)
    return cmdstrs