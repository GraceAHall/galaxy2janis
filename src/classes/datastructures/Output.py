

# pyright: strict


from xml.etree import ElementTree as et
import re

from classes.datastructures.Params import Param
from utils.etree_utils import get_attribute_value
from utils.galaxy_utils import consolidate_types


class Output:
    def __init__(self, node: et.Element, params: list[Param]) -> None:
        self.node = node
        self.name: str = ''
        self.params = params
        self.janis_var: str = '' 
        self.galaxy_type: str = ''
        self.janis_type: str = ''
        self.selector: str = ''
        self.selector_contents: str = ''
        self.help_text: str = ''  # ?
        self.is_hidden: bool = False
        self.is_array: bool = False

        self.extension_mappings = {
            'fasta': ['fa', 'fna', 'fasta'],
            'fastq': ['fq', 'fastq']
        }


        # i dont understand "metadata_source"
        # discover_datasets should be janis WildcardSelector with datatype = j.Array(j.File)


    def __str__(self) -> str:
        galaxy_type = self.galaxy_type
        return f'{self.name[-29:]:<30}{galaxy_type[-24:]:>25}{self.selector[-19:]:>20}{self.selector_contents[-19:]:>20}{self.is_array:>15}'


    def parse(self) -> None:
        self.set_basic_details()
        self.set_help_text()
        self.galaxy_type = self.get_datatype()
        self.galaxy_type = consolidate_types(self.galaxy_type)
        self.set_selector_contents()
        self.set_is_array()
        self.set_janis_var()


    def set_basic_details(self) -> None:
        self.name = get_attribute_value(self.node, 'name')
        if get_attribute_value(self.node, 'hidden') == 'true':
            self.is_hidden = True


    def set_help_text(self) -> None:
        label = get_attribute_value(self.node, 'label')
        if "${on_string}" in label:
            label = label.rsplit("${on_string}", 1)[1]
            label = label.strip(':')
            label = label.strip(' ')
            self.help_text = label
        

    # override
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


    def set_janis_var(self) -> None:
        pass

    
    def get_datatype(self) -> str:
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
            datatype = self.get_datatype_from_param(format_source)

        # get datatype from referenced file extension
        elif from_work_dir != '':
            assert('.' in from_work_dir)
            datatype = from_work_dir.rsplit('.', 1)[1]

        # fallback
        else:
            datatype = 'File'

        return datatype


    def get_datatype_from_param(self, format_source: str) -> str:
        # not working
        for param in self.params:
            if format_source == param.name:
                return param.galaxy_type
        
        return '' # failed
        #raise Exception(f'could not find param: {format_source}')


    def format_pattern_extension(self, pattern: str) -> str:
        # get datatypes
        datatype_list = self.galaxy_type.split(',')
        
        # check if the pattern already ends with any of these datatypes
        for datatype in datatype_list:
            
            # get all possible extensions for the datatype
            if datatype in self.extension_mappings:
                extensions = self.extension_mappings[datatype]
            else:
                extensions = [datatype]

            # check if any are present
            for ext in extensions:
                if pattern.endswith('.' + ext):
                    return pattern

        # if not, add the first to the pattern end (if not file)
        pattern = pattern.rstrip('.')
        if len(datatype_list) == 1 and datatype_list[0] == 'file':
            return pattern
        pattern = pattern + '.' + datatype_list[0]
        
        return pattern



class WorkdirOutput(Output):
    def __init__(self, node: et.Element, params: list[Param]) -> None:
        super().__init__(node, params)
        self.selector = "WildcardSelector"


    def set_selector_contents(self) -> None:
        pattern = get_attribute_value(self.node, 'from_work_dir')
        pattern = self.format_pattern_extension(pattern)
        self.selector_contents = pattern



class DiscoverDatasetsOutput(Output):
    def __init__(self, node: et.Element, params: list[Param]) -> None:
        super().__init__(node, params)
        self.selector = "WildcardSelector"


    # overrides base class
    def get_datatype(self) -> str:
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
            return gx_format

        # get datatype from referenced param
        elif format_source != '':
            return self.get_datatype_from_param(format_source)

        dd_node = self.node.find('discover_datasets')
        dd_format = get_attribute_value(dd_node, 'format') # type: ignore
        dd_ext = get_attribute_value(dd_node, 'ext') # type: ignore

        if dd_format != '':
            return dd_format

        elif dd_ext != '':
            return dd_ext
        
        return 'file'


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


    def transform_pattern(self, pattern: str) -> str:
        transformer = {
            '__designation__': '*',
            '.*?': '*',
            '\\.': '.',
        }

        # # remove anything in brackets
        # pattern_list = pattern.split('(?P<designation>')
        # if len(pattern_list) == 2:
        #     pattern_list[1] = pattern_list[1].split(')', 1)[-1]

        # find anything in between brackets
        bracket_strings = re.findall("\\((.*?)\\)", pattern)

        # remove brackets & anything previously found (lazy)
        pattern = pattern.replace('(', '').replace(')', '')
        for the_string in bracket_strings:
            if '<ext>' in the_string:
                pattern = pattern.replace(the_string, '') # lazy and bad
            pattern = pattern.replace(the_string, '*')

        for key, val in transformer.items():
            pattern = pattern.replace(key, val)

        # remove regex start and end patterns
        pattern = pattern.rstrip('$').lstrip('^')
        return pattern



class TemplatedOutput(Output):
    def __init__(self, node: et.Element, params: list[Param]) -> None:
        super().__init__(node, params)
        self.selector = "InputSelector"
        self.input_param = self.link_input_param()


    def link_input_param(self) -> Param:
        for param in self.params:
            if param.name == self.node.attrib['name']:
                return param
        raise Exception(f'could not link TemplatedOutput to its input param: {self.node.attrib["name"]}')


    def set_selector_contents(self) -> None:
        """
        just sets to generated input param name
        """
        self.selector_contents = f'{self.input_param.name}'
    





# class CollectionOutput(Output):
#     def __init__(self, node: et.Element, params: list[Param]) -> None:
#         super().__init__(node, params)
#         pass

#     def set_datatype(self) -> None:
#         pass
    

#     def set_selector(self) -> None:
#         pass