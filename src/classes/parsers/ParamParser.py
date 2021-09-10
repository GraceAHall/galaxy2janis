

from copy import deepcopy
from collections import Counter

from classes.datastructures.Params import Param, TextParam, IntParam, FloatParam, DataParam, BoolParam, SelectParam, DataCollectionParam, DataColumnParam, HiddenParam
from classes.Logger import Logger
from xml.etree import ElementTree as et



class ParamParser:
    """
    iterates through xml tree nodes, parsing params if encountered. 
    """
    
    def __init__(self, tree: et.ElementTree, command_lines: list[str]):
        # other helper classes
        self.logger: Logger = Logger()   
        self.tree: et.ElementTree = tree
        self.command_lines = command_lines
        self.param_list: list[Param] = []
        self.params: dict[str, Param] = {}

        self.galaxy_depth_elems = ['conditional', 'section']
        self.parsable_elems = ['param']  # just param for now
        self.ignore_elems = ['macros', 'requirements', 'version_command', 'command', 'tests', 'help', 'citations', 'test']

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

    
    def parse(self) -> None:
        # parse params
        tree_path = []
        for node in self.tree.getroot():
            self.explore_node(node, tree_path)

        # remove dups
        self.remove_duplicate_params()

    
    def explore_node(self, node: et.Element, prev_path: list[str]) -> None:
        # would this extend the galaxy variable path?
        curr_path = deepcopy(prev_path)
        if node.tag in self.galaxy_depth_elems:
            curr_path.append(node.attrib['name'])

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
            new_param = self.parse_param(node, tree_path)
            self.param_list.append(new_param)

        #elif node.tag == 'repeat':  TODO!
        #    self.parse_repeat(node, tree_path)


    def parse_param(self, node: et.Element, tree_path: list[str]) -> Param:
        """
        parses a param elem. accepts a tree node, returns a new Param
        RESTRUCTURE!


        each param subclass gets:
         - parent node
         - command lines (incl conditionals)
        
        Method
        initialize_params()
        

        for each param:
         - param.parse():
         - param.parse_basic_details()
         - param.parse_ 
            - parse_
         - param.parse_datatype()
         - param.parse_datatype()


        """

        params = self.initialize_params(node, tree_path)
        for param in params:
            param.parse()
 

    def initialize_params(self, node: et.Element, tree_path: list[str]) -> list[Param]:
        # get param type
        param_type = node.attrib['type']

        # params we can initalize immediately
        if param_type in ['text', 'color']:
            return [TextParam(node, tree_path, self.command_lines)]

        elif param_type == 'integer':
            return [IntParam(node, tree_path, self.command_lines)]

        elif param_type == 'data':
            return [DataParam(node, tree_path, self.command_lines)]

        elif param_type == 'data_collection':
            raise Exception('wtf error: param type="data_collection"')
            return [DataCollectionParam(node, tree_path, self.command_lines)]

        elif param_type == 'data_column':
            raise Exception('wtf error: param type="data_column"')
            return [DataColumnParam(node, tree_path, self.command_lines)]

        elif param_type == 'hidden':
            raise Exception('wtf error: param type="hidden"')
            return [HiddenParam(node, tree_path, self.command_lines)]

        # params which need more processing and potential splitting
        elif param_type == 'boolean':
            new_params = self.initialize_bool_params(node, tree_path)
            return new_params

        elif param_type == 'select':
            new_params = self.initialize_select_params(node, tree_path)
            return new_params
    

    def initialize_bool_params(self, node: et.Element, tree_path: list[str]) -> list[Param]:
        tv = node.attrib['truevalue'] or ''  #TODO bring back get_attribute_value()
        fv = node.attrib['falsevalue'] or ''  #TODO bring back get_attribute_value()

        if self.is_flag_param_list([tv, fv]):
            # create 2 flag bools
            label = node.attrib['label'] or ''
            param1 = self.create_bool_node(tv, label)
            param2 = self.create_bool_node(fv, label)
            return [param1, param2]
        else:
            return [BoolParam(node, tree_path, self.command_lines)]
        

        return []


    def initialize_select_params(self, node: et.Element, tree_path: list[str]) -> list[Param]:
        options = self.get_select_options(node)

        # should split into flag bools
        if self.is_flag_param_list(options):
            params = []

            for opt in options:
                temp_node = self.create_bool_node(opt['value'], opt['text'])
                params.append(BoolParam(temp_node, tree_path, self.command_lines))
            return params
            
        # dont split
        else:
            return [SelectParam(node, tree_path, self.command_lines)]            


    def get_select_options(self, node: et.Element) -> list[dict]:
        options = []

        for child in node:
            if child.tag == 'option':
                opt = {'value': child.attrib['value'], 'text': child.text or ''}
                options.append(opt)
        
        return options


    def create_bool_node(self, val: str, text: str) -> et.Element:
        attributes = {
            'argument': val,
            'label': text,
            'type': 'boolean',
            'checked': 'False',
            'truevalue': val,
            'falsevalue': ''
        }
        node = et.Element('param', attributes)
        return node


    # write test?
    def is_flag_param_list(self, options: list[str]) -> bool:
        outcome = True

        # check all the options start with '-'
        for opt in options:
            if not opt['value'].startswith('-'):
                outcome = False
                break

        # ensure its just not because negative numbers
        try: 
            [float(opt['value']) for opt in options] 
            outcome = False  # if reaches this point, all opts are float castable
        except ValueError:
            pass

        return outcome


    def parse_repeat(self, node, tree_path):
        pass


    def remove_duplicate_params(self) -> None:
        clean_params = {}

        for query_param in self.param_list:
            if query_param.gx_var not in clean_params:
                clean_params[query_param.gx_var] = query_param
            else:
                ref_param = clean_params[query_param.gx_var]
                self.assert_duplicate_param(query_param, ref_param)
                
        self.params = clean_params


    def assert_duplicate_param(self, query, ref) -> None:
        assert(query.type == ref.type)
        assert(query.default_value == ref.default_value)
        assert(query.prefix == ref.prefix)
        assert(query.help_text == ref.help_text)
        assert(query.is_optional == ref.is_optional)
        assert(query.is_argument == ref.is_argument)
        assert(query.is_array == ref.is_array)
        assert(query.options == ref.options)
        