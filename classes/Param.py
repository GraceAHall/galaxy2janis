
# pyright: strict

from collections import Counter
from classes.Logger import Logger
from xml.etree import ElementTree

# Optional[str] means the type can be str or None. 

class Param:
    def __init__(self, node: ElementTree.Element, local_path: list[str]):
        # other helper classes
        self.logger: Logger = Logger()   
        self.node = node

        # param attributes
        self.name: str = ""
        self.type: str = ""
        self.local_path = local_path
        self.default_value: str = ""
        self.prefix: str = ""
        self.help_text: str = ""
        self.is_optional: bool = False
        self.is_argument: bool = False
        self.is_ui_param: bool = False

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
        self.set_basic_details()
        self.set_argument_info()


    def set_basic_details(self) -> None:
        # basic info
        self.name = self.get_attribute_value('name')
        self.default_value = self.get_attribute_value('value')
        self.help_text = self.get_attribute_value('help')

        # is param optional?
        if self.get_attribute_value('optional') == "true":
            self.is_optional = True


    def set_argument_info(self) -> None:
        # is param an argument param?
        if self.get_attribute_value('argument') is not None:
            self.is_argument = True

            # set name and prefix accordingly
            argument = self.get_attribute_value('argument')
            self.name = argument.lstrip('-').replace('-', '_') 
            self.prefix = argument 
            
        
    def infer_janis_type(self) -> None:
        """
        try to guess the real param datatype as would appear in janis tool description. 
        not an exact science due to galaxy flexability.

        if this is too unreliable, can ask simon to get list of successful jobs for each tool. 
        would then check what the variable is resolved to in the job script. can identify if its text, or a specific datatype if the argument is always a file with a particular extension.

        janis "file" type is good fallback. 
        """

        galaxy_type = self.get_attribute_value('type')
        if galaxy_type in self.parseable_datatypes:
            if galaxy_type == "text":
                self.type = "string"  # don't differentiate between single string and comma-separated. User can read helptext for usage. 
            elif galaxy_type == "integer":
                self.type = "integer"
            elif galaxy_type == "float":
                self.type = "float"
            elif galaxy_type == "boolean":
                pass
            elif galaxy_type == "select":
                self.type = self.extract_type_from_select_param()
            elif galaxy_type == "color":
                self.type = "string"  # usually color name or #hexcode
            elif galaxy_type == "data_column":
                pass
            elif galaxy_type == "hidden":
                pass
            elif galaxy_type == "data":
                self.type = self.extract_type_from_data_param()
            elif galaxy_type == "data_collection":
                self.type = self.extract_type_from_data_collection_param()
        else:
            self.logger.log(1, f'could not extract type from {galaxy_type} param')

        # format attribute only applies to 'data' and 'data_collection' types


        """
        data often tells you the exact type. 
        The main types needed to resolve is the command line params.
        File can be a good fallback here.
        
        eg --fasta: 
         - is this single string referring to a filename, array?
         - can we assume this has to be a fasta input? 
         - if this is tricky, can ask simon to get list of successful jobs for each tool. can check extensions of each input file. 

        text: string
        integer: integer
        float: float

        boolean: 
         - normal bool, but additionally has truevalue and falseval. map of 0/1 to strings
         - are the strings always text, or do they sometimes map to integers or floats? 
         - probably a good idea to collect all examples of this. 
 
        genomebuild # never used
        select
        color
        data_column
        hidden
        hidden_data # never used
        baseurl # rarely used
        file # rarely used
        ftpfile # never used
        data:
         - for tool io
         - dataset from history
         - 'format' determines datatype - format can be comma-separated list so multiple types. eg bamOrSamFile -> bam,sam. Is galaxy doing type conversion here? 
         - some galaxy datatypes need to be mapped to real datatypes. eg interval -> BED? 
         - multiple="true" specifies array of files as input
         - select parameters with multiple="true": also are arrays
         - group_tag never used

        data_collection
        library_data # never used
        drill_down # never used
        """

    def extract_type_from_select_param(self) -> str:
        """
        infers select param type. 
        Uses the different values in the option elems 
        """
        for child in self.node:
            if child.tag == 'option':
                
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
      

    def get_local_path(self) -> str:
        local_path = '.'.join(self.local_path)
        if local_path == '':
            return self.name
        else:
            return local_path + f'.{self.name}'


    def get_attribute_value(self, attribute: str) -> str:
        '''
        accepts node, returns attribute value or None 
        '''
        for key, val in self.node.attrib.items():
            if key == attribute:
                return val
        return ""


    def print(self):
        print('\nclass: param')
        print(f'name: {self.name}')
        print(f'local_path: {self.local_path}')
        print(f'type: {self.type}')
        print(f'prefix: {self.prefix}')
        print(f'default: {self.default_value}')
        print(f'help_text: {self.help_text}')
        print(f'is_optional: {self.is_optional}')
        print(f'is_argument: {self.is_argument}')
        print(f'is_ui_param: {self.is_ui_param}')