

# pyright: basic


from xml.etree import ElementTree as et
import re

from galaxy_tool.param.ParamRegister import ParamRegister
from utils.etree_utils import get_attribute_value
#from utils.galaxy_utils import consolidate_types


class Output:
    def __init__(self, node: et.Element) -> None:
        # tree things
        self.node = node

        # details to parse
        self.name: str = ''
        self.gx_var: str = ''
        self.galaxy_type: str = ''
        self.datatypes: list[dict[str, str]] = []
        self.help_text: str = ''  # ?
        self.is_optional: bool = False 
        self.is_array: bool = False
        self.is_hidden: bool = False
        self.is_stdout: bool = False
        self.selector: str = ''
        self.selector_contents: str = ''

        self.extension_mappings = {
            'fasta': ['fa', 'fna', 'fasta'],
            'fastq': ['fq', 'fastq']
        }

        # i dont understand "metadata_source"
        # discover_datasets should be janis WildcardSelector with datatype = j.Array(j.File)


    def __str__(self) -> str:
        datatype = self.galaxy_type
        subclass = self.__class__.__name__
        return f'{self.name[-29:]:30}{datatype[-14:]:15}{subclass[-19:]:20}{self.is_array:5}'


    def parse(self) -> None:
        self.set_basic_details()
        self.set_help_text()
        self.set_selector_contents()
        self.set_is_array()


    def set_basic_details(self) -> None:
        self.name = get_attribute_value(self.node, 'name')
        self.gx_var = self.name
        if get_attribute_value(self.node, 'hidden') == 'true':
            self.is_hidden = True


    def set_help_text(self) -> None:
        label = get_attribute_value(self.node, 'label')
        if "${on_string}" in label:
            label = label.rsplit("${on_string}", 1)[1]
            label = label.strip(':')
            label = label.strip(' ')
            self.help_text = label
        

    # override method
    def set_selector_contents(self) -> None:
        pass


    def set_is_array(self) -> None:
        # has * in WildcardSelector
        if '*' in self.selector_contents:
            self.is_array = True
        
        # root is <data>, but has <discover_datasets> child
        elif self.node.tag == 'data':
            if self.node.find('discover_datasets') is not None:
                self.is_array = True

        # root is <collection>
        elif self.node.tag == 'collection':
            self.is_array = True      

    
    def set_datatype(self, param_register: ParamRegister) -> str:
        # datatype can be specified in format, format_source, auto_format (ext), or from_work_dir.
        gx_format = get_attribute_value(self.node, 'format')
        format_source = get_attribute_value(self.node, 'format_source')
        from_work_dir = get_attribute_value(self.node, 'from_work_dir')
        #auto_format = get_attribute_value(self.node, 'auto_format')
        
        # easiest & most common option
        if gx_format != '':
            datatype = gx_format

        # get datatype from referenced param
        elif format_source != '':
            varname, param = param_register.get(format_source)
            return param.galaxy_type

        # get datatype from referenced file extension
        elif from_work_dir != '':
            # TODO HERE needs a much more complex process to get datatype from extension. 
            # needs a map of extensions -> galaxy types
            # this isn't even a datatype - its an ext being returned? so bad yuck 
            datatype = 'file'
            # datatype = from_work_dir.rsplit('.', 1)[-1]

        # fallback
        else:
            datatype = 'file'

        self.galaxy_type = datatype


    def format_pattern_extension(self, filepath: str) -> str:
        # get datatypes
        datatype_list = self.galaxy_type.split(',')
        datatype_list = [d for d in datatype_list if d != '']

        # early exits
        if len(datatype_list) == 1 and datatype_list[0] == 'File':
            return filepath
        elif len(datatype_list) == 0:
            return filepath
        
        # check if the filepath already ends with any of these datatypes
        for datatype in datatype_list:
            
            # get all possible extensions for the datatype
            if datatype in self.extension_mappings:
                extensions = self.extension_mappings[datatype]
            else:
                extensions = [datatype]

            # check if any are present
            for ext in extensions:
                if filepath.endswith('.' + ext):
                    return filepath

        # if not, add the first to the filepath end (if not file)
        filepath = filepath.rsplit('.', 1)[0]
        filepath = filepath + '.' + datatype_list[0]
        return filepath


    def get_default_value(self):
        return ''



class WorkdirOutput(Output):
    def __init__(self, node: et.Element) -> None:
        super().__init__(node)
        self.selector = "WildcardSelector"


    def set_selector_contents(self) -> None:
        pattern = get_attribute_value(self.node, 'from_work_dir')
        pattern = self.format_pattern_extension(pattern)
        self.selector_contents = pattern



class DiscoverDatasetsOutput(Output):
    def __init__(self, node: et.Element) -> None:
        super().__init__(node)
        self.selector = "WildcardSelector"


    # overrides base class
    def set_datatype(self, param_register: ParamRegister) -> str:
        """
        in <collection> or <data>(parent):
            - format
            - format_source

        in <discover_datasets>:
            - format
            - ext (both aliases of each other)

        or none at all! datatype currently left as File in this case. 
        """
        gx_format = get_attribute_value(self.node, 'format')
        format_source = get_attribute_value(self.node, 'format_source')

        # easiest & most common option
        if gx_format != '':
            self.galaxy_type = gx_format

        # get datatype from referenced param
        elif format_source != '':
            varname, param = param_register.get(format_source)
            if param is not None:
                self.galaxy_type = param.galaxy_type

        else:
            dd_node = self.node.find('discover_datasets')
            dd_format = get_attribute_value(dd_node, 'format') # type: ignore
            dd_ext = get_attribute_value(dd_node, 'ext') # type: ignore

            if dd_format != '':
                self.galaxy_type = dd_format

            elif dd_ext != '':
                self.galaxy_type = dd_ext
        
        self.galaxy_type = 'file'


    def set_selector_contents(self) -> None:
        dd_node = self.node.find('discover_datasets')
        directory = get_attribute_value(dd_node, 'directory') # type: ignore
        pattern = self.extract_pattern(dd_node) # type: ignore
        pattern = self.format_pattern_extension(pattern) 
        self.selector_contents = f'{directory}/{pattern}'

    
    def extract_pattern(self, node: et.Element) -> str:
        pattern = get_attribute_value(node, 'pattern') # type: ignore
        pattern = self.transform_pattern(pattern)
        return pattern






class TemplatedOutput(Output):
    def __init__(self, node: et.Element) -> None:
        super().__init__(node)
        self.selector = "InputSelector"


    def set_selector_contents(self) -> None:
        """
        just sets to generated input param name
        """
        self.selector_contents = f'{self.name}'
    



# class CollectionOutput(Output):
#     def __init__(self, node: et.Element) -> None:
#         super().__init__(node)
#         pass

#     def set_datatype(self) -> None:
#         pass
    

#     def set_selector(self) -> None:
#         pass