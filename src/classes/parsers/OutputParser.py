



from xml.etree import ElementTree as et

from classes.datastructures.Output import Output, DataOutput, DiscoverDatasetsOutput
from classes.datastructures.Params import Param


class OutputParser:
    def __init__(self, tree: et.ElementTree, params: list[Param]) -> None:
        self.tree = tree
        self.params = params
        self.parsable_elems: list[str] = ['data', 'collection']
        self.outputs: list[Output] = [] 

    
    def parse(self) -> list[Output]:
        output_elems = self.get_all_outputs()
        
        outputs = []
        for node in output_elems:
            if node.tag == 'data':
                new_output = DataOutput(node, self.params)
                new_output.parse()
                outputs.append(new_output)

        return outputs


    def get_all_outputs(self) -> list[et.Element]:
        root = self.tree.getroot()
        output_section = root.find('outputs')

        outputs = []
        for child in output_section:
            if child.tag in self.parsable_elems:
                outputs.append(child)

        return outputs


    def initialize_output(self) -> Output:
        pass


    def initialize_data_output(self) -> Output:
        pass


    def initialize_discover_datasets_output(self) -> Output:
        pass