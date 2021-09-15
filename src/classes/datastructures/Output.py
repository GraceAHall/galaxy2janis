

# pyright: strict


from xml.etree import ElementTree as et

from classes.datastructures.Params import Param
from utils.etree_utils import get_attribute_value
from utils.galaxy_utils import convert_extensions

class Output:
    def __init__(self, node: et.Element, params: list[Param]) -> None:
        self.node = node
        self.params = params
        self.name: str = ''  #  janis tag
        self.datatype: str = ''
        self.selector: str = ''
        self.selector_contents: str = ''
        self.help_text: str = ''  # ?
        self.is_hidden: bool = False
        # i dont understand "metadata_source"
        # discover_datasets should be janis WildcardSelector with datatype = j.Array(j.File)


    def parse(self) -> None:
        self.set_basic_details()
        self.set_help_text()
        self.datatype = self.get_datatype()
        self.set_selector()


    def set_basic_details(self) -> None:
        self.name = get_attribute_value(self.node, 'name')
        if get_attribute_value(self.node, 'hidden') == 'true':
            self.is_hidden = True


    def set_help_text(self) -> None:
        # no idea what this should be yet
        pass


    def get_datatype(self) -> str:
        # sets from format, format_source, auto_format (ext), from_work_dir
        # needs heirarchy
        gx_format = get_attribute_value(self.node, 'format')
        format_source = get_attribute_value(self.node, 'format_source')
        from_work_dir = get_attribute_value(self.node, 'from_work_dir')
        auto_format = get_attribute_value(self.node, 'auto_format')
        
        # best option
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
        elif auto_format != '':
            return 'File'

        else:
            raise Exception(f"can't get datatype for {self.node.attrib['name']}")


    def get_datatype_from_param(self, format_source: str) -> str:
        for param in self.params:
            if format_source == param.gx_var:
                return param.datatype
        raise Exception(f'could not find param: {format_source}')


    def set_selector(self) -> None:
        """
        janis.InputSelector
         - Used for selecting input params
         - links output to something specified in params
         - 
        janis.WildcardSelector - Used for collecting outputs (discover_datasets)
        janis.StringFormatter - Constructing or transforming strings
        
        # outputs are often just a template which appears in the command string. galaxy (presumeably) just assigns a temp var and links them. eg 
        
        fastp input.fa > ${out} 
        <data name='out' format='fasta' label='{tool.name} on.. fastaout' />

        value of ${out} doesnt mean anything really. could make it = var1 and just capture var1 as that output. its all anonymous dataset.dat anyway. 
        
        create an input param for each templated output. 
        user can choose the filename or it defaults to out1, out2 with extension added. then in the output, janis.InputSelector is used to link to that filename set by the user. 
        
        # may have to create input params for situations where an output is just templated
        # from_work_dir -> StringFormatter
        # <discover_datasets> -> WildcardSelector
        #   - pattern, directory, ext, format, 
        # WildcardSelector: if * in pattern, output has to be Array
        
        """

        # simple specifying the output file. use StringFormatter. 
        from_work_dir_text = get_attribute_value(self.node, 'from_work_dir')
        if from_work_dir_text != '':
            self.selector = 'StringFormatter'
            self.selector_contents = from_work_dir_text
            return

        # attempt to instead find a discover_datasets child. Use WildcardSelector.
        # assert there is only a single discover_datasets child
        dd_list = self.node.findall('discover_datasets')
        assert(len(dd_list) < 2)
        if len(dd_list) == 1:
            dd = dd_list[0]
            
            self.datatype = get_attribute_value()
            pattern = dd_list[0], '')
        pass


    



class DataOutput(Output):
    def __init__(self, node: et.Element, params: list[Param]) -> None:
        super().__init__(node, params)
        pass


class DiscoverDatasetsOutput(Output):
    def __init__(self, node: et.Element, params: list[Param]) -> None:
        super().__init__(node, params)
        pass
    

class CollectionOutput(Output):
    def __init__(self, node: et.Element, params: list[Param]) -> None:
        super().__init__(node, params)
        pass