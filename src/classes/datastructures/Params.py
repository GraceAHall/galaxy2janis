
# pyright: basic

# Optional[str] means the type can be str or None. 

from xml.etree import ElementTree as et
from typing import Optional

from classes.Logger import Logger
from classes.VariableFinder import VariableFinder, VariableReference # type: ignore

from utils.galaxy import get_common_extension, convert_extensions, cast_list, get_attribute_value


# missing logging: logger.log_unknown_type(1, item)

class Param:
    def __init__(self, node: et.Element, tree_path: list[str], cmd_lines: list[str]):
        self.logger = Logger()
        self.node = node
        self.tree_path = tree_path
        self.cmd_lines = cmd_lines

        # basic info for each Param subclass
        self.name: str = ''
        self.gx_var: str = ''
        self.datatype: str = ''
        self.default_value: str = ''
        self.help_text: str = ''
        self.is_optional: bool = False
        self.cmd_references: list[VariableReference] = []

        # checks
        self.has_command_ref: bool = False
        self.has_conditional_ref: bool = False
        self.is_argument: bool = False   

        # other bools (probably will delete)
        self.is_array: bool = False  # text?
        self.validated: bool = False

        # linking to command string
        self.prefix: Optional[str] = None

        # galaxy stuff
        self.truths = ['true', 'True']


    def parse_common_features(self) -> None:
        self.set_basic_details()
        self.set_gx_var()
        self.set_references()
        self.set_prefix()
        self.validate()
        

    def set_basic_details(self) -> None:
        # name & prefix 
        if get_attribute_value(self.node, 'argument') == '':
            self.name = get_attribute_value(self.node, 'name')
        else:
            argument = get_attribute_value(self.node, 'argument')
            self.name = argument.lstrip('-').replace('-', '_') 
            self.prefix = argument  # TODO find this in command pls
            self.is_argument = True

        # defaults    
        self.default_value = get_attribute_value(self.node, 'value')

        # help text
        self.set_help_text()
        
        # is optional
        if get_attribute_value(self.node, 'optional') in self.truths:
            self.is_optional = True


    def set_help_text(self) -> None:
        help_text = get_attribute_value(self.node, 'help')
        label = get_attribute_value(self.node, 'label')
        if help_text == '' and label != '':
            help_text = label
        self.help_text = help_text


    def set_gx_var(self) -> None:
        tree_path = '.'.join(self.tree_path)
        if tree_path == '':
            self.gx_var = self.name
        else:
            self.gx_var = tree_path + f'.{self.name}'


    def set_references(self) -> None:
        vf = VariableFinder(self.gx_var, self.cmd_lines) # type: ignore
        self.cmd_references = vf.find() # type: ignore
        self.set_cmd_ref_details()

    
    def set_cmd_ref_details(self) -> None:
        for ref in self.cmd_references:
            if ref.in_conditional:
                self.has_conditional_ref = True
            else:
                self.has_command_ref = True


    def set_prefix(self):
        """
        single occurance in cmd string (ref) usually (ignoring cheetah 
        conditional lines) 
        multiple refs need human decision.
        """
        cmd_refs = self.cmd_references 
        cmd_refs = [ref for ref in cmd_refs if not ref.in_conditional]  
        
        if len(cmd_refs) == 1:
            self.prefix = cmd_refs[0].prefix
        elif len(cmd_refs) > 1:
            self.prefix = self.user_select_prefix()
        
 
    def user_select_prefix(self) -> str:
        # print basics
        print('--- prefix selection ---')
        print(f'var: {self.gx_var}')
        print('possible prefixes:\n')

        # print each candidate prefix
        for i, ref in enumerate(self.cmd_references):
            print(f'reference {i}')
            print(ref)
        
        selected_elem = int(input('correct prefix (num)'))
        prefix = self.cmd_references[selected_elem].prefix
        return prefix
        

    def validate(self) -> None:
        # more to come? 
        try:
            assert(self.name != '')
            assert(self.gx_var != None)
            assert(self.node != None)
            assert(self.has_command_ref or self.has_conditional_ref)
            self.validated = True
        except AssertionError:
            print()


    def __str__(self):
        out_str = ''
        out_str += '\nparam --------------\n'

        out_str += f'gx_var: {self.gx_var}\n'
        out_str += f'prefix: {self.prefix}\n'
        out_str += f'datatype: {self.datatype}\n'
        out_str += f'default_value: {self.default_value}\n'
        out_str += f'help_text: {self.help_text}\n'
        out_str += f'is_optional: {self.is_optional}\n'
        out_str += f'has_command_ref: {self.has_command_ref}\n'
        out_str += f'validated: {self.validated}\n'

        return out_str



class TextParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str], cmd_lines: list[str]):
        super().__init__(node, tree_path, cmd_lines)
        # type="color" is also TextParam
        self.datatype: str = 'String' #?


    def parse(self) -> None:
        self.parse_common_features()



class IntParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str], cmd_lines: list[str]):
        super().__init__(node, tree_path, cmd_lines)
        self.datatype: str = 'Integer'


    def parse(self) -> None:
        self.parse_common_features()



class FloatParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str], cmd_lines: list[str]):
        super().__init__(node, tree_path, cmd_lines)
        self.datatype: str = 'Float'


    def parse(self) -> None:
        self.parse_common_features()



class DataParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str], cmd_lines: list[str]):
        super().__init__(node, tree_path, cmd_lines)
        self.datatype: str = ''


    def parse(self) -> None:
        self.parse_common_features()
        self.set_datatype()


    def set_datatype(self) -> None:
        gx_format = get_attribute_value(self.node, 'format')
        gx_datatypes = gx_format.split(',') 
        datatypes = convert_extensions(gx_datatypes)
        self.datatype = ','.join(datatypes)


class BoolParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str], cmd_lines: list[str]):
        super().__init__(node, tree_path, cmd_lines)
        self.datatype = 'Boolean'


    def parse(self) -> None:
        self.validate_value_order()
        self.parse_common_features()
        #self.set_flag()


    def validate_value_order(self) -> None:
        tv = get_attribute_value(self.node, 'truevalue')
        fv = get_attribute_value(self.node, 'falsevalue')
        if tv == '' and fv != '':
            self.node.attrib['truevalue'] = fv
            self.node.attrib['falsevalue'] = tv


    def set_prefix(self):
        self.prefix = get_attribute_value(self.node, 'truevalue')


    def set_flag(self) -> None:
        self.flag = get_attribute_value(self.node, 'truevalue')
        assert(self.flag != '')


class SelectParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str], cmd_lines: list[str]):
        super().__init__(node, tree_path, cmd_lines)
        self.options: list[str] = []
        self.select_type: str = ''  # the flavour of select param
    

    def parse(self) -> None:
        self.set_param_options()
        self.parse_common_features()
        self.set_datatype()
        self.add_options_to_helptext()


    def set_param_options(self) -> None:
        option_values = []

        for child in self.node:
            if child.tag == 'option':
                optval = get_attribute_value(child, 'value')
                option_values.append(optval)  # type: ignore

        self.options = option_values


    def set_datatype(self) -> None:
        """
        infers select param type. 
        Uses the different values in the option elems.
        param options are already stored in param.options
        """
        param_type = "String"  # fallback

        # are the option values all a particular type?
        castable_type = cast_list(self.options)

        # do the option values all have a common extension? 
        common_extension = get_common_extension(self.options)
        
        # deciding what the type should be from our results
        if common_extension != '':
            param_type = common_extension
        elif castable_type != '':
            param_type = castable_type

        self.datatype = param_type


    def add_options_to_helptext(self) -> None:
        options = ', '.join(self.options[:5])

        # trail off if more than 5 options...
        if len(self.options) > 5:
            options += '...' 

        self.help_text += f'  example values: {options}'



class DataCollectionParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str], cmd_lines: list[str]):
        super().__init__(node, tree_path, cmd_lines)


    def parse(self) -> None:
        pass



class DataColumnParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str], cmd_lines: list[str]):
        super().__init__(node, tree_path, cmd_lines)


    def parse(self) -> None:
        pass



class HiddenParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str], cmd_lines: list[str]):
        super().__init__(node, tree_path, cmd_lines)

    
    def parse(self) -> None:
        pass