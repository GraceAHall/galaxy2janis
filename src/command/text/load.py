

from runtime.settings.ExeSettings import ToolExeSettings
from galaxy_interaction import GalaxyManager
from xmltool.load import load_xmltool
from command.text.simplification import simplify_xml, simplify_xml_cheetah_eval, simplify_test 


# TODO alias resolving

def load_xml_command(esettings: ToolExeSettings) -> str:
    gxmanager = GalaxyManager(esettings)
    xmltool = load_xmltool(esettings)
    cmdstr = gxmanager.get_xml_cmdstr(xmltool)
    cmdstr = simplify_xml(cmdstr)
    return cmdstr

def load_xml_command_cheetah_eval(esettings: ToolExeSettings) -> str:
    gxmanager = GalaxyManager(esettings)
    xmltool = load_xmltool(esettings)
    cmdstr = gxmanager.get_xml_cmdstr(xmltool)
    cmdstr = simplify_xml_cheetah_eval(cmdstr)
    return cmdstr
    
def load_test_commands(esettings: ToolExeSettings) -> list[str]:
    cmdstrs: list[str] = []
    gxmanager = GalaxyManager(esettings)
    xmltool = load_xmltool(esettings)
    for teststr in gxmanager.get_test_cmdstrs(xmltool):
        teststr = simplify_test(teststr)
        cmdstrs.append(teststr)
    return cmdstrs