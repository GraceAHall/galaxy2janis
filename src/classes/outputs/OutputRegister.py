


from typing import Optional
from xml.etree import ElementTree as et


from galaxy.tool_util.parser.output_objects import ToolOutput
from copy import deepcopy


#from classes.outputs.Outputs import Output, WorkdirOutput


class OutputRegister:
    def __init__(self, outputs: dict) -> None:
        self.outputs: dict[str, str] = {}
        self.add_from_dict(outputs, [])


    def add_from_dict(self, outputs: dict, levels: list[str]) -> None:
        for label, obj in outputs.items():
            if hasattr(obj, 'outputs'):
                next_levels = deepcopy(levels)
                next_levels.append(obj.name)
                self.add_from_dict(obj.outputs, next_levels)
            else:
                if len(levels) == 0:
                    key = '$' + label
                else:
                    key = '$' + '.'.join(levels) + '.' + label
                if key not in self.outputs:
                    self.outputs[key] = obj


    def get(self, query_key: str) -> Optional[ToolOutput]:
        if query_key in self.outputs:
            return self.outputs[query_key]
        return None


    def get_outputs(self) -> list[ToolOutput]:
        return list(self.outputs.values())


    def get_output_by_filepath(self, filepath: str) -> Optional[ToolOutput]:
        # try to match the whole path
        for out in self.outputs.values():
            if out.selector_contents == filepath:
                return out
        
        # no success, try to match the end of the path
        for out in self.outputs.values():
            if out.selector_contents.endswith(filepath):
                return out

        # again no success, try to match the filepath anywhere in the selector contents
        for out in self.outputs.values():
            if filepath in out.selector_contents:
                return out

        return None


    def create_output_from_text(self, text: str) -> None:
        """
        creates a new output using a dummy et.Element
        the new et.Element node is populated with some default details
        then is parsed as normal created the new output. 
        the output is added to our collection of outputs. 
        """
        # create dummy node
        name = text.split('.', 1)[0]
        dummy_node = et.Element('data', attrib={'name': name, 'format': 'file', 'from_work_dir': text})
        
        # create and parse output
        new_output = ToolOutput(dummy_node)
        new_output.parse()

        # add to collection
        self.add([new_output])


    def restructure_outputs(self, outputs: list[ToolOutput]) -> None:
        output_dict = {}
        for out in self.outputs:
            key = '$' + out.gx_var
            output_dict[key] = out
        self.outputs = output_dict



