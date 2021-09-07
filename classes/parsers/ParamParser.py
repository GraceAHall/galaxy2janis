

from copy import deepcopy
from collections import Counter

from classes.datastructures.Param import Param
from classes.Logger import Logger
from xml.etree import ElementTree as et

"""
iterates through xml tree nodes, parsing params if encountered. 
"""

class ParamParser:
    def __init__(self, tree: et.ElementTree):
        # other helper classes
        self.logger: Logger = Logger()   
        self.tree = tree
        self.params = []

        self.galaxy_depth_elems = ['conditional', 'section']
        self.parsable_elems = ['param']

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

        self.janis_datatypes = [
            "BAI",
            "BAM",
            "bed",
            "BedGz",
            "BedTABIX",
            "Boolean",
            "CompressedIndexedVCF",
            "CompressedTarFile",
            "CompressedVCF",
            "CRAI",
            "CRAM",
            "CramPair",
            "csv",
            "Directory",
            "Double",
            "Fasta",
            "FastaBwa",
            "FastaFai",
            "FastaGz",
            "FastaGzBwa",
            "FastaGzFai",
            "FastaGzWithIndexes",
            "FastaWithIndexes",
            "FastDict",
            "FastGzDict",
            "Fastq",
            "FastqGz",
            "File",
            "Filename",
            "Float",
            "Gzip",
            "HtmlFile",
            "IndexedBam",
            "IndexedVCF",
            "Integer",
            "jsonFile",
            "KallistoIdx",
            "SAM",
            "Stdout",
            "String",
            "TarFile",
            "TextFile",
            "tsv",
            "VCF",
            "WhisperIdx",
            "Zip"
        ]


    def parse(self) -> None:
        tree_path = []
        for node in self.tree.iter():
            self.parse_node(node, tree_path)

    
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
            if self.should_descend(child):
                self.explore_node(child, curr_path)


    def should_descend(self, node: et.Element) -> bool:
        if node.tag in self.ignore_elems:
            return False
        return True


    def parse_elem(self, node: et.Element, tree_path: list[str]) -> None:
        if node.tag == 'param':
            new_param = self.parse_param(node, tree_path)
            self.param.append(new_param)
        #elif node.tag == 'repeat':  TODO!
        #    self.parse_repeat(node, tree_path)


    # public
    def parse_param(self, node: et.Element, tree_path: list[str]) -> Param:
        new_param = Param()
        new_param = self.set_basic_details(node, new_param)
        new_param = self.infer_janis_type(node, new_param)
        return new_param

    
    def set_basic_details(self, node: et.Element, param: Param) -> Param:
        # name (and prefix if argument param)
        if self.get_attribute_value(node, 'argument') == "":
            param.name = self.get_attribute_value(node, 'name')
        else:
            argument = self.get_attribute_value(node, 'argument')
            param.name = argument.lstrip('-').replace('-', '_') 
            param.prefix = argument 
            param.is_argument = True

        # defaults, optional, helptext    
        param.default_value = self.get_attribute_value(node, 'value')
        param.help_text = self.get_attribute_value(node, 'help')
        if self.get_attribute_value(node, 'optional') == "true":
            param.is_optional = True

        return param


    def get_attribute_value(self, node: et.Element, attribute: str) -> str:
        '''
        accepts node, returns attribute value or "" 
        '''
        for key, val in node.attrib.items():
            if key == attribute:
                return val
        return ""
    
        
    def infer_janis_type(self, node: et.Element, param: Param) -> Param:
        """
        good reporting here! 

        try to guess the real param datatype as would appear in janis tool description. 
        not an exact science due to galaxy flexability.

        if this is too unreliable, can ask simon to get list of successful jobs for each tool. 
        would then check what the variable is resolved to in the job script. can identify if its text, or a specific datatype if the argument is always a file with a particular extension.

        janis "file" type is good fallback. 
        
        format attribute only applies to 'data' and 'data_collection' types
        """

        galaxy_type = self.get_attribute_value(node, 'type')

        if galaxy_type in self.parseable_datatypes:
            if galaxy_type == "text":
                param.type = "string"  # don't differentiate between single string and comma-separated. User can read helptext for usage. 

            elif galaxy_type == "integer":
                param.type = "integer"

            elif galaxy_type == "float":
                param.type = "float"

            elif galaxy_type == "boolean":
                pass

            elif galaxy_type == "select":
                param.type = self.extract_type_from_select_param()

            elif galaxy_type == "color":
                param.type = "string"  # usually color name or #hexcode

            elif galaxy_type == "data_column":
                pass

            elif galaxy_type == "hidden":
                pass
            elif galaxy_type == "data":
                param.type = self.extract_type_from_data_param()

            elif galaxy_type == "data_collection":
                param.type = self.extract_type_from_data_collection_param()
        
        else:
            self.logger.log(1, f'could not extract type from {galaxy_type} param')

        return param


    def extract_type_from_select_param(self) -> str:
        """
        infers select param type. 
        Uses the different values in the option elems 
        """
        for child in self.node:
            if child.tag == 'option':
                pass  # do something
        return ""


    def extract_type_from_data_param(self) -> str:
        """
        datatype hints found in "format" attribute
        sometimes this will be all that's needed, other times we need to do more work. 
        If select: is this string
        """
        return ""


    def extract_type_from_data_collection_param(self) -> str:
        """
        """
        return ""


    def get_text_type(self):
        pass


    def get_select_type(self):
        # is single item or array? - multiple attribute
        # what datatype are the items? - try to cast_param_values, if all strings see if they have shared extension? get extension list. 
        pass


    def cast_param_values(self):
        pass


    def can_cast_to_string(self):
        pass


    def can_cast_to_float(self):
        pass 


    def can_cast_to_int(self):
        pass


    def get_shared_extension(self, the_list: list[str]) -> str: 
        """
        identifies whether a list of items has a common extension. 
        all items must share the same extension. 
        will return the extension if true, else will return ""
        """

        try:
            ext_list = [item.rsplit('.', 1)[1] for item in the_list]
            exts = Counter(ext_list)
        except IndexError:  # one or more items do not have an extension
            return "" 
           
        if len(exts) == 1:  
            ext, count = exts.popitem() 
            if count == len(the_list):  # does every item have the extension?
                return ext 

        return ""
      

    def parse_repeat(self, node, tree_path):
        pass