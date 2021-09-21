



from xml.etree import ElementTree as et

from classes.Logger import Logger
from classes.datastructures.Output import Output, WorkdirOutput, DiscoverDatasetsOutput, TemplatedOutput
from classes.datastructures.Params import Param, OutputParam
from utils.etree_utils import get_attribute_value, create_output_param


class OutputParser:
    def __init__(self, tree: et.ElementTree, params: list[Param], command_lines: list[str], logger: Logger) -> None:
        self.tree = tree
        self.params = params
        self.command_lines = command_lines
        self.logger = logger
        self.parsable_elems: list[str] = ['data', 'collection']
        self.outputs: list[Output] = [] 

    
    def parse(self) -> list[Output]:
        output_elems = self.get_all_outputs()
        
        # initialize all outputs
        outputs = []
        for node in output_elems:
            if node.tag in self.parsable_elems:
                new_output = self.initialize_output(node)
                outputs.append(new_output)

        # parse all outputs
        for output in outputs:
            output.parse()
            self.log_pattern_status(output)

        self.outputs = outputs
        return self.outputs


    def log_pattern_status(self, output: Output) -> None:
        banned_substrings = ['?', '+', '<ext>', '[', ']', '(', ')']
        pattern = output.selector_contents
        for substr in banned_substrings:
            if substr in pattern:
                self.logger.log(1, 'complex regex')
                break

    
    def get_all_outputs(self) -> list[et.Element]:
        root = self.tree.getroot()
        output_section = root.find('outputs')

        outputs = []
        for child in output_section:
            if child.tag in self.parsable_elems:
                outputs.append(child)

        return outputs


    def initialize_output(self, node: et.Element) -> Output:
        """
        receives any output node, then delegates initialization to the right output subclass initialization function.
        """
        output_type = self.get_output_type(node)

        if output_type == 'workdir':
            return self.initialize_workdir_output(node)
        elif output_type == 'discover':
            return self.initialize_discover_datasets_output(node)
        elif output_type == 'templated':
            return self.initialize_templated_output(node)
        else:
            raise Exception(f'output type not known for node: {node.attrib["name"]}')
        

    def get_output_type(self, node: et.Element) -> str:
        if get_attribute_value(node, 'from_work_dir') != '':
            return 'workdir'
        elif node.find('discover_datasets') is not None:
            return 'discover'
        else:
            # validate: locate the output name in the command string
            return 'templated'


    def initialize_workdir_output(self, node: et.Element) -> Output:
        """
        initializes a WorkdirOutput. WorkdirOutput has the most simple parse() method. used when from_work_dir is set. 
        """
        return WorkdirOutput(node, self.params)
    

    def initialize_discover_datasets_output(self, node: et.Element) -> Output:
        """
        initializes a DiscoverDatasetsOutput. this subclass has a different parse() method as it must extract info from child nodes. 
        """
        return DiscoverDatasetsOutput(node, self.params)


    def initialize_templated_output(self, node: et.Element) -> Output:
        """
        initializes a TemplatedOutput. TemplatedOutputs need to create an input param to reference.
        """
        # create dummy param for the output to refer to
        temp_out_node = create_output_param(node)

        # initialize new param & parse
        output_param = self.initialize_output_param(temp_out_node)
        
        # update params with new param
        self.params.append(output_param)

        # return new output with reference to updated params
        return TemplatedOutput(node, self.params)


    def initialize_output_param(self, node: et.Element) -> Param:
        new_param = OutputParam(node, [], self.command_lines)
        new_param.parse()
        return new_param


    def pretty_print(self) -> None:
        print('\n--- Outputs ---\n')
        print(f'{"name":<30}{"datatype":>25}{"selector":>20}{"selector_contents":>20}{"collection":>15}')
        print('-' * 110)
        for output in self.outputs:
            print(output)


    # def initialize_collection_output(self, node: et.Element) -> Output:
    #     """
    #     initializes a CollectionOutput. 
    #     """
    #     pass