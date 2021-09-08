

from copy import deepcopy
from collections import Counter

from classes.datastructures.Params import Param
from classes.Logger import Logger
from xml.etree import ElementTree as et

"""
iterates through xml tree nodes, parsing params if encountered. 
"""

class ParamParser:
    def __init__(self, tree: et.ElementTree):
        # other helper classes
        self.logger: Logger = Logger()   
        self.tree: et.ElementTree = tree
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
        """

        # changed order! parse the command string before params!!!


        param = Param(node, tree_path)
        new_params = param.parse()

        print(new_params)

        # kill this stufff
        self.set_basic_details(node, new_param)
        self.handle_edge_cases(node, new_param)
        self.infer_janis_type(node, new_param)

        return new_param


    def handle_edge_cases(self, node: et.Element, param: Param) -> None:
        # booleans
        if self.get_attribute_value(node, 'type') == 'boolean':
            self.handle_bool_param(node, param)
        
        # selects
        if self.get_attribute_value(node, 'type') == 'select':
            self.handle_select_param(node, param) 


    # move to BoolParam
    def handle_bool_param(self, node: et.Element, param: Param) -> None:
        """
        This should actually be 'handle_bool()' or something

        possible types:

        true bool
         - no truevalue / falsevalue 
         - can only be UI param

        flag bool 
         - either truevalue or falsevalue are str & start with '-' or '--'
         - the other value is blank str
         - interpret as flag boolean

        2 value select bool
         - both truevalue and falsevalue are set
         - both do not begin with '-' or '--'
         - interpret as string param, add both options to helptext: "options: tv or fv"

        2 value flag bool
         - both truevalue and falsevalue are set
         - both begin with either '-' or '--'
         - break into 2 individual flag bools

        weird bool
         - one of truevalue or falsevalue are set
         - it does not start with '--' or '-'
         - interpret as flag bool for now. TODO
        """

        truevalue = self.get_attribute_value(node, 'truevalue')
        falsevalue = self.get_attribute_value(node, 'falsevalue')

        #true bool (UI param)
        if truevalue == '' and falsevalue == '':
            pass

        #flag bool
        if truevalue.startswith('-') and falsevalue == '':
            pass
        elif falsevalue.startswith('-') and truevalue == '':
            pass

        # 2 value select bool


    # move to SelectParam
    def handle_select_param(self, node: et.Element, param: Param) -> None:
        param.options = self.get_param_options(node)


    def infer_janis_type(self, node: et.Element, param: Param) -> None:
        """
        try to guess the real param datatype as would appear in janis tool description. 

        more reporting here?
        """

        gx_type = self.get_attribute_value(node, 'type')

        if gx_type in self.parseable_datatypes:
            # straight conversions
            if gx_type in ['text', 'integer', 'float', 'color']:
                param.datatype = self.gx_janis_datatype_mapping[gx_type]

            # special cases
            elif gx_type == "data":
                param.datatype = self.get_data_elem_type(node)

            elif gx_type == "boolean":
                param.datatype = self.get_bool_elem_type(node)
            
            elif gx_type == "select":
                if self.get_attribute_value(node, 'multiple') == 'true':
                    param.is_array == True
                param.datatype = self.get_select_elem_type(param)

            elif gx_type == "data_collection":
                raise Exception('wtf error: param type="data_collection"')
                
            elif gx_type == "data_column":
                raise Exception('wtf error: param type="data_column"')  # TODO

            elif gx_type == "hidden":
                raise Exception('wtf error: param type="hidden"')  # TODO
            
        else:
            self.logger.log(1, f'could not extract type from {gx_type} param')

        if param.datatype == '':
            print()
        


    def get_select_elem_type(self, param: Param) -> str:
        """
        infers select param type. 
        Uses the different values in the option elems.
        param options are already stored in param.options
        """
        param_type = "String"  # fallback

        # are the option values all a particular type?
        castable_type = self.cast_list(param.options)

        # do the option values all have a common extension? 
        common_extension = self.get_common_extension(param.options)
        
        # deciding what the type should be from our results
        if common_extension != '':
            param_type = common_extension
        elif castable_type != '':
            param_type = castable_type

        return param_type


    def get_data_elem_type(self, node: et.Element) -> str:
        """
        datatype hints found in "format" attribute
        sometimes this will be all that's needed, other times we need to do more work. 
        """ 
        type_list = self.get_attribute_value(node, 'format').split(',')
        type_list = self.convert_extensions(type_list)
        type_list = list(set(type_list))

        return ','.join(type_list)


    def cast_list(self, the_list: list[str]) -> str:
        """
        identifies whether all list items can be cast to a common datatype.
        currently just float and int
        """
        castable_types = []

        if self.can_cast_to_float(the_list):
            castable_types.append('Float')
        elif self.can_cast_to_int(the_list):
            castable_types.append('Integer')

        if 'Float' in castable_types:
            if 'Integer' in castable_types:
                return 'Integer'
            else:
                return 'Float'

        return ''


    def can_cast_to_float(self, the_list: list[str]) -> bool:
        for item in the_list:
            try:
                float(item)
            except ValueError:
                return False
        return True 


    def can_cast_to_int(self, the_list: list[str]) -> bool:
        for item in the_list:
            if item[0] in ('-', '+'):
                item = item[1:]

            if not item.isdigit():
                return False

        return True 


    def get_common_extension(self, the_list: list[str]) -> str: 
        """
        identifies whether a list of items has a common extension. 
        all items must share the same extension. 
        will return the extension if true, else will return ""
        """
        
        try:
            ext_list = [item.rsplit('.', 1)[1] for item in the_list]
        except IndexError:
            return ''  # at least one item has no extension

        ext_list = self.convert_extensions(ext_list)
        ext_counter = Counter(ext_list)
           
        if len(ext_counter) == 1:  
            ext, count = ext_counter.popitem() 
            if count == len(the_list):  # does every item have the extension?
                return ext 

        return ""
      

    def convert_extensions(self, the_list: list[str]) -> list[str]:
        """
        converts galaxy extensions to janis. 
        also standardises exts: fastqsanger -> Fastq, fastq -> Fastq. 
        """
        out_list = []
        for item in the_list:
            if item in self.gx_janis_datatype_mapping:
                ext = self.gx_janis_datatype_mapping[item]
            else:
                self.logger.log_unknown_type(1, item)
                ext = 'String'  # fallback pretty bad but yeah. 
            out_list.append(ext)

        return out_list


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
        