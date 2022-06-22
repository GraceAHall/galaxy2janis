

import os
from typing import Optional
import gx.utils.etree as etree_utils 

def get_xml_by_tool_id(xmldir: str, query_id: str) -> Optional[str]:
    xmls = [x for x in os.listdir(xmldir) if x.endswith('.xml') and 'macros' not in x]
    for xml in xmls:
        filepath = f'{xmldir}/{xml}'
        tool_id = etree_utils.get_xml_tool_id(filepath)
        if query_id == tool_id:
            return xml
    return None