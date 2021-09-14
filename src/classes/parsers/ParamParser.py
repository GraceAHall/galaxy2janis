

from copy import deepcopy
from collections import Counter

from classes.datastructures.Params import Param, TextParam, IntParam, FloatParam, DataParam, BoolParam, SelectParam, DataCollectionParam, DataColumnParam, HiddenParam
from classes.Logger import Logger
from xml.etree import ElementTree as et
from utils.galaxy import get_attribute_value, get_param_name



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

        # remove dup params
        for param in self.param_list:
            print(param)
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
            return []
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
        out_params = []

        # get bool values
        tv = get_attribute_value(node, 'truevalue')
        fv = get_attribute_value(node, 'falsevalue')

        # reformatting for standard function call
        trueopt = {'value': tv, 'text': ''}
        falseopt = {'value': fv, 'text': ''}

        # check if should split bool into 2 bools
        if self.is_flag_param_list([trueopt, falseopt]):
            label = node.attrib['label'] or ''
            out_params.append(self.create_bool_elem(node, tv, label))
            out_params.append(self.create_bool_elem(node, fv, label))

        # check if actually 2 option select
        elif self.is_string_list([trueopt, falseopt]):
            select_node = self.convert_bool_to_select_elem(node)
            out_params += self.initialize_select_params(select_node) 

        # is normal bool
        else:
            out_params.append(BoolParam(node, tree_path, self.command_lines))

        return out_params


    # TODO untested
    def is_string_list(self, the_list: list[str]) -> bool:
        """
        string list is list of values which do not look like prefixes ('-' at start)
        """
        for item in the_list:
            val = item['value']
            if val == '' or val[0] == '-':
                return False
        return True


    # TODO untested
    def convert_bool_to_select_elem(self, node: et.Element) -> et.Element:
        # convert param attributes
        attributes = {
            'type': 'select',
            'name': get_attribute_value(node, 'name'),
            'label': get_attribute_value(node, 'label'),
            'help': get_attribute_value(node, 'help'),
            'multiple': 'False'
        }
        parent = et.Element('param', attributes)

        # create child option for each bool value
        tv = get_attribute_value(node, 'truevalue')
        fv = get_attribute_value(node, 'falsevalue')

        for val in [tv, fv]:
            attributes = {'value': val}
            child = et.Element('option', attributes)
            parent.append(child)
        
        return parent


    def get_attribute_value(self, node: et.Element, attribute: str) -> str:
        '''
        accepts node, returns attribute value or "" 
        '''
        for key, val in node.attrib.items():
            if key == attribute:
                return val
        return ""

    def initialize_select_params(self, node: et.Element, tree_path: list[str]) -> list[Param]:
        out_params = []

        # get options list
        options = self.get_select_options(node)

        # check if should split into flag bools
        if self.is_flag_param_list(options):
            bool_elems = self.convert_select_to_bool_elems(node)
            for elem in bool_elems:
                out_params.append(BoolParam(elem, tree_path, self.command_lines))
                
        # no split
        else:
            out_params.append(SelectParam(node, tree_path, self.command_lines)) 

        return out_params     


    def get_select_options(self, node: et.Element) -> list[dict]:
        options = []

        for child in node:
            if child.tag == 'option':
                opt = {'value': child.attrib['value'], 'text': child.text or ''}
                options.append(opt)
        
        return options


    def convert_select_to_bool_elems(self, node: et.Element) -> list[et.Element]:
        out_elems = []
        
        options = self.get_select_options(node)
        for opt in options:
            bool_elem = self.create_bool_elem(node, opt['value'], opt['text'])
            out_elems.append(bool_elem)

        return out_elems


    def create_bool_elem(self, node: et.Element, val: str, text: str) -> et.Element:
        # bool elem
        attributes = {
            'name': get_attribute_value(node, 'name'),
            'argument': get_attribute_value(node, 'argument'),
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


    def parse_repeat_elem(self, node, tree_path):
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
        