


import os
from Bio import pairwise2
import utils.etree as etree_utils 


def global_align(pattern: str, template: str) -> int:
    pattern = pattern.lower()
    template = template.lower()
    outcome = pairwise2.align.globalms(pattern, template, 2, -1, -.5, -.1) # type: ignore
    if len(outcome) > 0: # type: ignore
        score = outcome[0].score # type: ignore
    else:
        score = 0
    return score # type: ignore

def is_int(the_string: str) -> bool:
    if the_string.isdigit():
        return True
    return False

def is_float(the_string: str) -> bool:
    if not is_int(the_string):
        try:
            float(the_string)
            return True
        except ValueError:
            pass
    return False

def select_xmlfile(xmldir: str, query_id: str) -> str:
    xmls = [x for x in os.listdir(xmldir) if x.endswith('.xml') and 'macros' not in x]
    if len(xmls) == 0:  # if no xmls, theres some error
        raise RuntimeError(f'no tool xml files in {xmldir}')
    elif len(xmls) == 1: # if only 1 valid xml, return
        return xmls[0]
    else: # else, open each and look at the tool_id and match to esettings
        for xml in xmls:
            filepath = f'{xmldir}/{xml}'
            tool_id = etree_utils.get_xml_tool_id(filepath)
            if query_id == tool_id:
                return xml
        raise RuntimeError(f'cant find tool xml matching {query_id}')