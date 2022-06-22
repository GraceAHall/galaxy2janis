

import json
import xml.etree.ElementTree as et

def is_galaxy_workflow(path: str) -> bool:
    """checks that the provided path is a galaxy workflow"""
    with open(path, 'r') as fp:
        data = json.load(fp)
    if data['a_galaxy_workflow'] == 'true':
        return True
    return False

def is_tool_xml(path: str) -> bool:
    """checks that the provided path is tool xml"""
    root = et.parse(path).getroot()
    if root.tag == 'tool':
        return True
    return False