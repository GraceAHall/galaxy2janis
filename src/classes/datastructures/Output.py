

# pyright: strict


from xml.etree import ElementTree as et

from classes.datastructures.Params import Param
from utils.etree_utils import get_attribute_value
from utils.galaxy_utils import convert_extensions


class Output:
    def __init__(self, node: et.Element, params: list[Param]) -> None:
        self.node = node
        self.params = params
        self.janis_var: str = '' 
        self.datatype: str = ''
        self.selector: str = ''
        self.selector_contents: str = ''
        self.help_text: str = ''  # ?
        self.is_hidden: bool = False
        self.is_collection: bool = False

        # i dont understand "metadata_source"
        # discover_datasets should be janis WildcardSelector with datatype = j.Array(j.File)


    def parse(self) -> None:
        self.set_basic_details()
        self.set_help_text()
        self.datatype = self.get_datatype()
        self.set_selector_contents()
        self.set_is_collection()
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


    def set_is_collection(self) -> None:
        # has * in WildcardSelector
        if '*' in self.selector_contents:
            self.is_collection = True
        
        # root is <data>, but has <discover_datasets> child
        elif self.node.tag == 'data':
            if self.node.find('discover_datasets') is not None:
                self.is_collection = True

        # root is <collection>
        elif self.node.tag == 'collection':
            self.is_collection = True        


    def set_janis_var(self) -> None:
        pass

    
    def get_datatype(self) -> str:
        # datatype can be specified in format, format_source, auto_format (ext), or from_work_dir.
        gx_format = get_attribute_value(self.node, 'format')
        format_source = get_attribute_value(self.node, 'format_source')
        from_work_dir = get_attribute_value(self.node, 'from_work_dir')
        auto_format = get_attribute_value(self.node, 'auto_format')
        
        # easiest & most common option
        if gx_format != '':
            format_list = gx_format.split(',')
            datatypes = convert_extensions(format_list)
            return ','.join(datatypes)

        # get datatype from referenced param
        elif format_source != '':
            return self.get_datatype_from_param(format_source)

        # get datatype from referenced file extension
        elif from_work_dir != '':
            assert('.' in from_work_dir)
            return from_work_dir.rsplit('.', 1)[1]

        # fallback
        # TODO log warning
        else:
            return 'File'


    def get_datatype_from_param(self, format_source: str) -> str:
        for param in self.params:
            if format_source == param.name:
                return param.datatype
        raise Exception(f'could not find param: {format_source}')



class WorkdirOutput(Output):
    def __init__(self, node: et.Element, params: list[Param]) -> None:
        super().__init__(node, params)
        self.selector = "WildcardSelector"


    def set_selector_contents(self) -> None:
        self.selector_contents = get_attribute_value(self.node, 'from_work_dir')



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
            format_list = gx_format.split(',')
            datatypes = convert_extensions(format_list)
            return ','.join(datatypes)

        # get datatype from referenced param
        elif format_source != '':
            return self.get_datatype_from_param(format_source)

        dd_node = self.node.find('discover_datasets')
        dd_format = get_attribute_value(dd_node, 'format') # type: ignore
        dd_ext = get_attribute_value(dd_node, 'ext') # type: ignore

        if dd_format != '':
            format_list = dd_format.split(',')
            datatypes = convert_extensions(format_list)
            return ','.join(datatypes)

        # get datatype from referenced param
        elif dd_format != '':
            return self.get_datatype_from_param(dd_format)
        
        return 'File'


    def set_selector_contents(self) -> None:
        dd_node = self.node.find('discover_datasets')
        directory = get_attribute_value(dd_node, 'directory') # type: ignore
        pattern = self.extract_pattern(dd_node)
        pattern = self.format_pattern_extension(dd_node)

    
    def extract_pattern(self, node: et.Element) -> str:
        pattern = get_attribute_value(node, 'pattern') # type: ignore
        pattern = self.transform_pattern(pattern)
        return pattern


    def transform_pattern(self, pattern: str) -> str:
        transformer = {
            '__designation__': '*',
            '\\.': '.',
        }

        # remove anything in brackets containing designation pattern
        pattern_list = pattern.split('(?P<designation>')
        if len(pattern_list) == 2:
            pattern_list[1] = pattern_list[1].split(')', 1)[-1]

        pattern = pattern_list[0] + '*' + pattern_list[1]
        # perform replacements
        for key, val in transformer.items():
            pattern = pattern.replace(key, val)

        pattern = pattern.rstrip('$').lstrip('^')
        return pattern


    def format_pattern_extension(self, dd_node: et.Element) -> str:
        pass



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
        pattern=""
        directory=""
        visible="false" (default), is same as hidden
        """
        pass
    





# class CollectionOutput(Output):
#     def __init__(self, node: et.Element, params: list[Param]) -> None:
#         super().__init__(node, params)
#         pass

#     def set_datatype(self) -> None:
#         pass
    

#     def set_selector(self) -> None:
#         pass