


from typing import Optional
from xml.etree import ElementTree as et

from classes.outputs.Outputs import Output, WorkdirOutput


class OutputRegister:
    def __init__(self) -> None:
        self.outputs: dict[str, Output] = {}


    def add(self, outputs: list[Output]) -> None:
        for out in outputs:
            key = '$' + out.gx_var
            if key not in self.outputs:
                self.outputs[key] = out


    def get(self, query_key: str) -> Optional[Output]:
        if query_key in self.outputs:
            return self.outputs[query_key]
        return None


    def get_outputs(self) -> list[Output]:
        return list(self.outputs.values())


    def get_output_by_filepath(self, filepath: str) -> Optional[Output]:
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
        new_output = WorkdirOutput(dummy_node)
        new_output.parse()

        # add to collection
        self.add([new_output])


    def restructure_outputs(self, outputs: list[Output]) -> None:
        output_dict = {}
        for out in self.outputs:
            key = '$' + out.gx_var
            output_dict[key] = out
        self.outputs = output_dict



