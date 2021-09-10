
# pyright: strict

# Optional[str] means the type can be str or None. 

from xml.etree import ElementTree as et

from classes.Logger import Logger
from classes.PrefixCollector import PrefixCollector

from utils.galaxy import get_common_extension, convert_extensions


# missing logging: logger.log_unknown_type(1, item)

class Param:
    def __init__(self, node: et.Element, tree_path: list[str], command_lines: list[str]):
        self.logger = Logger()
        self.node = node
        self.tree_path = tree_path
        self.command_lines = command_lines

        # basic info for each Param subclass
        self.name: str = ''
        self.gx_var: str = ''
        self.default_value: str = ''
        self.help_text: str = ''
        self.is_optional: bool = False

        # checks
        self.located_in_command: bool = False
        self.appears_in_conditional: bool = False
        self.is_ui_param: bool = False  
        self.is_argument: bool = False   

        # bools (probably will delete)
        self.is_array: bool = False  

        # linking to command string
        self.prefix_collector = PrefixCollector()
        self.prefix: str = ''

        # galaxy stuff
        self.truths = ['true', 'True']
        

    def set_basic_details(self) -> None:
        if self.get_attribute_value(self.node, 'argument') == '':
            self.name = self.get_attribute_value(self.node, 'name')
        else:
            argument = self.get_attribute_value(self.node, 'argument')
            self.name = argument.lstrip('-').replace('-', '_') 
            self.prefix = argument  # TODO find this in command pls
            self.is_argument = True

        # defaults, optional, helptext    
        self.default_value = self.get_attribute_value(self.node, 'value')
        self.help_text = self.get_attribute_value(self.node, 'help')
        if self.get_attribute_value(self.node, 'optional') in self.truths:
            self.is_optional = True


    def get_attribute_value(self, node: et.Element, attribute: str) -> str:
        '''
        accepts node, returns attribute value or "" 
        '''
        for key, val in self.node.attrib.items():
            if key == attribute:
                return val
        return ""


    def set_gx_var(self) -> None:
        tree_path = '.'.join(self.tree_path)
        if tree_path == '':
            self.gx_var = self.name
        else:
            self.gx_var = tree_path + f'.{self.name}'


    # hmmmmm
    def resolve_multiple_prefixes(self) -> None:
        if len(self.prefix_collector.prefixes) > 1:
            self.prefix_collector.user_select_prefix()


    # hmmmmm
    def set_prefix_from_collector(self) -> None:
        assert(len(self.prefix_collector.prefixes) in [0, 1])

        if len(self.prefix_collector.prefixes) == 1:
            if self.prefix != '':  # no idea if this would happen 
                raise Exception('prefix is set but trying to set from PrefixCollector')
            else:
                self.prefix = self.prefix_collector.prefixes[0].text
          

    def __str__(self):
        out_str = ''
        out_str += '\nparam --------------\n'

        for key, val in dir(self):
            out_str += f'{key}:\t{val}\n'

        return out_str



class TextParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str], command_lines: list[str]):
        super().__init__(node, tree_path, command_lines)
        # type="color" is also TextParam
        self.datatype: str = 'String' #?


    # generic structure
    def parse(self) -> None:
        self.set_basic_details()
        self.set_type()
        self.locate_in_command()
        self.set_prefix()
        self.validate()

        # returns list of generated Janis Params from the galaxy param
        return self.params






class IntParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str], command_lines: list[str]):
        super().__init__(node, tree_path, command_lines)
        self.datatype: str = 'Integer'


    def parse(self) -> None:
        pass



class FloatParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str], command_lines: list[str]):
        super().__init__(node, tree_path, command_lines)
        self.datatype: str = 'Float'


    def parse(self) -> None:
        pass



class DataParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str], command_lines: list[str]):
        super().__init__(node, tree_path, command_lines)
        self.datatype: str = ''


    def parse(self) -> None:
        pass


    def set_datatype(self):
        pass

    # ?
    def validate(self):
        # for each param, param gets the command string & attempts to 
        # find itself
        pass


    def set_prefix(self):
        # param uses command string to find its --prefix (if correct param subclass)  uses PrefixCollector? 
        pass



class BoolParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str], command_lines: list[str]):
        super().__init__(node, tree_path, command_lines)


    def parse(self) -> None:
        pass


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



class SelectParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str], command_lines: list[str]):
        super().__init__(node, tree_path, command_lines)
        self.options: list[str] = []
        self.select_type: str = ''  # the flavour of select param
        self.get_param_options()
    

    def parse(self) -> None:
        pass


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
        common_extension = get_common_extension(param.options)
        
        # deciding what the type should be from our results
        if common_extension != '':
            param_type = common_extension
        elif castable_type != '':
            param_type = castable_type

        return param_type


    def get_param_options(self) -> None:
        option_values = []

        for child in self.node:
            if child.tag == 'option':
                optval = self.get_attribute_value(child, 'value')
                option_values.append(optval)  # type: ignore

        self.options = option_values



class DataCollectionParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str], command_lines: list[str]):
        super().__init__(node, tree_path, command_lines)


    def parse(self) -> None:
        pass



class DataColumnParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str], command_lines: list[str]):
        super().__init__(node, tree_path, command_lines)


    def parse(self) -> None:
        pass



class HiddenParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str], command_lines: list[str]):
        super().__init__(node, tree_path, command_lines)

    
    def parse(self) -> None:
        pass