

from copy import deepcopy
from xml.etree import ElementTree as et

from classes.Logger import Logger
from classes.datastructures.Params import (
    Param, 
    TextParam, 
    IntParam, 
    FloatParam, 
    DataParam, 
    BoolParam, 
    SelectParam, 
    DataCollectionParam, 
    HiddenParam
) 
from utils.galaxy_utils import is_flag_list, is_string_list
from utils.etree_utils import ( 
    get_attribute_value, 
    get_select_options,
    create_bool_elem, 
    convert_bool_to_select_elem, 
    convert_select_to_bool_elems, 
)


class ParamParser:
    """
    iterates through xml tree nodes, initializing param subclass if encountered.
    most operations are imported from utils files.  
    actual parsing of the param is delegated to the Param class. 
    """
    
    def __init__(self, tree: et.ElementTree, command_lines: list[str], logger: Logger):
        # other helper classes
        self.tree: et.ElementTree = tree
        self.command_lines = command_lines
        self.logger = logger
        self.param_list: list[Param] = []
        self.params: dict[str, Param] = {}

        self.galaxy_depth_elems = ['conditional', 'section']
        self.parsable_elems = ['param']  # just param for now
        self.ignore_elems = ['macros', 'requirements', 'version_command', 'command', 'tests', 'help', 'citations', 'test', 'xml', 'macro', 'outputs']

        # for param type extraction 
        self.parseable_datatypes = [
            "text",
            "integer", 
            "float",
            "boolean",
            "select",
            "color",
            "data_column",
            "hidden",
            "data",
            "data_collection"
        ]


    # rename explore_tree?
    def parse(self) -> list[Param]:
        # parse params
        tree_path = []
        root = self.tree.getroot()
        inputs_node = root.find('inputs')

        if inputs_node is None:
            raise Exception('no <inputs> node found in tool xml')

        for node in inputs_node:
            self.explore_node(node, tree_path)

        self.check_param_command_refs()

        return self.param_list


    def check_param_command_refs(self) -> None:
        for param in self.param_list:
            if not param.has_command_ref and not param.has_conditional_ref:
                self.logger.log(1, 'variable not found in command string')

    
    def explore_node(self, node: et.Element, prev_path: list[str]) -> None:
        # would this extend the galaxy variable path?
        curr_path = deepcopy(prev_path)
        if node.tag in self.galaxy_depth_elems:
            curr_path.append(node.attrib['name'])

        if get_attribute_value(node, 'name') == 'first_assembly_iter_param':
            pass
        # Should we parse this node or just continue?
        if node.tag in self.parsable_elems:
            self.parse_elem(node, curr_path)

        # descend to child nodes (recursive)
        for child in node:
            if self.should_parse(child):
                self.explore_node(child, curr_path)


    def should_parse(self, node: et.Element) -> bool:
        if node.tag in self.ignore_elems:
            return False
        return True


    def parse_elem(self, node: et.Element, tree_path: list[str]) -> None:
        if node.tag == 'param':
            new_params = self.parse_param_elem(node, tree_path)
            self.param_list += new_params

        #elif node.tag == 'repeat':  TODO!
        #    self.parse_repeat_elem(node, tree_path)


    def parse_param_elem(self, node: et.Element, tree_path: list[str]) -> Param:
        """
        parses a param elem. 
        
        accepts a tree node, returns one or more fully parsed Params (select and boolean params may be split into multiple Params depending on contents). 

         - the number of params needed and their types are determined
         - Param subclass objects are initialized
         - control is passed to the Param which dictates its own methods of parsing the elem and looking up information in the command string
        """

        params = self.initialize_params(node, tree_path)
        for param in params:
            param.parse()

        return params
 

    def initialize_params(self, node: et.Element, tree_path: list[str]) -> list[Param]:
        """
        switch function to initialize params depending on type
        """
        # get param type
        param_type = node.attrib['type']

        # params we can initalize immediately
        if param_type in ['text', 'color']:
            return [TextParam(node, tree_path, self.command_lines)]

        elif param_type == 'integer':
            return [IntParam(node, tree_path, self.command_lines)]
        
        elif param_type == 'float':
            return [FloatParam(node, tree_path, self.command_lines)]

        elif param_type == 'data':
            return [DataParam(node, tree_path, self.command_lines)]

        elif param_type == 'data_collection':
            return [DataCollectionParam(node, tree_path, self.command_lines)]

        elif param_type == 'data_column':
            return [TextParam(node, tree_path, self.command_lines)]

        elif param_type == 'hidden':
            self.logger.log(2, 'unsupported param type: hidden')
            return []
            return [HiddenParam(node, tree_path, self.command_lines)]

        # params which need more processing and potential splitting
        elif param_type == 'boolean':
            new_params = self.initialize_bool_params(node, tree_path)
            return new_params

        elif param_type == 'select':
            new_params = self.initialize_select_params(node, tree_path)
            return new_params
    

    def initialize_bool_params(self, node: et.Element, tree_path: list[str]) -> list[Param]:
        out_params = []

        # get bool values
        tv = get_attribute_value(node, 'truevalue')
        fv = get_attribute_value(node, 'falsevalue')

        # reformatting for standard function call
        trueopt = {'value': tv, 'text': ''}
        falseopt = {'value': fv, 'text': ''}

        # check if should split bool into 2 bools
        if is_flag_list([trueopt, falseopt]):
            label = node.attrib['label'] or ''
            # break into 2 et.Elements
            tv_node = create_bool_elem(node, tv, label)
            fv_node = create_bool_elem(node, fv, label)
            # create a BoolParam for each elem
            out_params.append(BoolParam(tv_node, tree_path, self.command_lines))
            out_params.append(BoolParam(fv_node, tree_path, self.command_lines))

        # check if actually 2 option select
        elif is_string_list([trueopt, falseopt]):
            select_node = convert_bool_to_select_elem(node)
            out_params += self.initialize_select_params(select_node, tree_path) 

        # is normal bool
        else:
            out_params.append(BoolParam(node, tree_path, self.command_lines))

        return out_params


    def initialize_select_params(self, node: et.Element, tree_path: list[str]) -> list[Param]:
        out_params = []

        # get options list
        options = get_select_options(node)

        # check if should split into flag bools
        if is_flag_list(options):
            bool_elems = convert_select_to_bool_elems(node)
            for elem in bool_elems:
                out_params.append(BoolParam(elem, tree_path, self.command_lines))
                
        # no split
        else:
            out_params.append(SelectParam(node, tree_path, self.command_lines)) 

        return out_params


    def parse_repeat_elem(self, node, tree_path):
        pass


    def pretty_print(self) -> None:
        print('\n--- Params ---\n')
        print(f'{"name":50}{"datatype":25}{"prefix":20}{"command":>10}')
        print('-' * 105)
        for param in self.param_list:
            print(param)


        