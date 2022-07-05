

from gx.gxtool.load import load_xmltool
from shellparser.text.simplification import ( 
    simplify_xml, 
    simplify_xml_cheetah_eval, 
)

def load_xml_command() -> str:
    xmltool = load_xmltool()
    cmdstr = xmltool.raw_command
    cmdstr = simplify_xml(cmdstr)
    return cmdstr

def load_xml_command_cheetah_eval() -> str:
    xmltool = load_xmltool()
    cmdstr = xmltool.raw_command
    cmdstr = simplify_xml_cheetah_eval(cmdstr)
    return cmdstr