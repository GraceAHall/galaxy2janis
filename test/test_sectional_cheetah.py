


from typing import Any
import json
import unittest
import xml.etree.ElementTree as et

from workflows.step.parsing.ToolStateFlattener import ToolStateFlattener
from workflows.step.parsing.inputs import get_flattened_tool_state
from workflows.step.parsing.inputs import standardise_tool_state
from command.manipulation.template.template import sectional_template

def read_cmd(path: str) -> str:
    tree = et.parse(path)
    root = tree.getroot()
    assert(root.text)
    return root.text

def read_step_inputs(path: str) -> dict[str, Any]:
    with open(path, 'r') as fp:
        step = json.load(fp)
    step['tool_state'] = json.loads(step['tool_state'])
    step['tool_state'] = get_flattened_tool_state(step)
    step['tool_state'] = standardise_tool_state(step)
    return step['tool_state']

unicycler_vanilla_path = 'test/data/command/manipulation/template/unicycler/unicycler_command.xml'
unicycler_templated_path = 'test/data/command/manipulation/template/unicycler/unicycler_command_templated.xml'
unicycler_inputs_path = 'test/data/command/manipulation/template/unicycler/unicycler_step.json'


class TestSectionalCheetah(unittest.TestCase):

    def test_unicycler(self):
        vanilla = read_cmd(unicycler_vanilla_path)
        reference = read_cmd(unicycler_templated_path)
        inputs = read_step_inputs(unicycler_inputs_path)
        templated = sectional_template(vanilla, inputs)
        self.assertEquals(reference, templated)


        