

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

        self.gx_janis_datatype_mapping = {
            "bai": "BAI",
            "bam": "BAM",
            "bed": "bed",
            "bed.gz": "BedGz",
            "tabix": "BedTABIX",
            "bool": "Boolean",
            "tar.gz": "CompressedTarFile",
            "brai": "CRAI",
            "cram": "CRAM",
            "CramPair": "CramPair",
            "csv": "csv",
            "directory": "Directory",
            "double": "Double",
            "fa": "Fasta",
            "fna": "Fasta",
            "fasta": "Fasta",
            "FastaBwa": "FastaBwa",  # TODO
            "fai": "FastaFai",  
            "fasta.gz": "FastaGz",
            "FastaGzBwa": "FastaGzBwa",  # TODO
            "FastaGzFai": "FastaGzFai",  # TODO
            "FastaGzWithIndexes": "FastaGzWithIndexes",
            "FastaWithIndexes": "FastaWithIndexes",
            "FastDict": "FastDict",
            "FastGzDict": "FastGzDict",
            "fq": "Fastq",
            "fastq": "Fastq",
            "fastqsanger": "Fastq",
            "fastqillumina": "Fastq",
            "fastq.gz": "FastqGz",
            "fastqsanger.gz": "FastqGz",
            "fastqillumina.gz": "FastqGz",
            "file": "File",
            "filename": "Filename",
            "float": "Float",
            "gz": "Gzip",
            "html": "HtmlFile",
            "IndexedBam": "IndexedBam",  # TODO
            "integer": "Integer",
            "json": "jsonFile",
            "kallisto.idx": "KallistoIdx",
            "sam": "SAM",
            "stdout": "Stdout",
            "string": "String",
            "tar": "TarFile",
            "txt": "TextFile",
            "tsv": "tsv",
            "vcf": "VCF",
            "vcf_bgzip": "CompressedVCF",
            "IndexedVCF": "IndexedVCF",  # TODO
            "CompressedIndexedVCF": "CompressedIndexedVCF", # TODO?
            "WhisperIdx": "WhisperIdx", # TODO
            "zip": "Zip"
        }


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
        """
        new_param = Param(tree_path)
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
            param.prefix = argument # currently do not attempt to find alternate prefix in command string for argument params.  may need to do this for cheetah function parsing. 
            param.is_argument = True

        # defaults, optional, helptext    
        param.default_value = self.get_attribute_value(node, 'value')
        param.help_text = self.get_attribute_value(node, 'help')
        if self.get_attribute_value(node, 'optional') == "true":
            param.is_optional = True

        # options if select param
        if self.get_attribute_value(node, 'type') == 'select':
            param.options = self.get_param_options(node)

        param.gx_var = param.get_tree_path()

        return param


    def get_attribute_value(self, node: et.Element, attribute: str) -> str:
        '''
        accepts node, returns attribute value or "" 
        '''
        for key, val in node.attrib.items():
            if key == attribute:
                return val
        return ""
    

    def get_param_options(self, node: et.Element) -> list[str]:
        option_values = []

        for child in node:
            if child.tag == 'option':
                optval = self.get_attribute_value(child, 'value')
                option_values.append(optval)

        return option_values



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
                # don't differentiate between single string and comma-separated. User can read helptext for usage. 
                param.type = "String"  

            elif galaxy_type == "integer":
                param.type = "Integer"

            elif galaxy_type == "float":
                param.type = "Float"

            elif galaxy_type == "boolean":
                param.type = "String"  # TODO! this is a fallback

            elif galaxy_type == "select":
                if self.get_attribute_value(node, 'multiple') == 'true':
                    param.is_array == True
                param.type = self.get_select_elem_type(param)

            elif galaxy_type == "color":
                param.type = "String"  # usually color name or #hexcode

            elif galaxy_type == "data_column":
                pass  # TODO

            elif galaxy_type == "hidden":
                pass  # TODO
            
            elif galaxy_type == "data":
                param.type = self.get_data_elem_types(node)

            elif galaxy_type == "data_collection":
                param.is_array == True  # ?
                param.type = self.get_data_collection_elem_types(node)
        
        else:
            self.logger.log(1, f'could not extract type from {galaxy_type} param')

        if param.type == '':
            print()
        return param


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


    def get_data_elem_types(self, node: et.Element) -> list[str]:
        """
        datatype hints found in "format" attribute
        sometimes this will be all that's needed, other times we need to do more work. 
        """ 
        type_list = self.get_attribute_value(node, 'format').split(',')
        type_list = self.convert_extensions(type_list)
        type_list = list(set(type_list))

        return ','.join(type_list)


    def get_data_collection_elem_types(self, node: et.Element) -> str:
        """
        TODO later
        """
        return ""


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
        