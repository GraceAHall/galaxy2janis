
# pyright: basic

# Optional[str] means the type can be str or None. 

from xml.etree import ElementTree as et
from typing import Optional

from classes.Logger import Logger
from classes.VariableFinder import VariableFinder, VariableReference # type: ignore

from utils.galaxy_utils import get_common_extension, cast_list, consolidate_types
from utils.etree_utils import get_attribute_value



class Param:
    def __init__(self, node: et.Element, tree_path: list[str], cmd_lines: list[str]):
        self.node = node
        self.tree_path = tree_path
        self.cmd_lines = cmd_lines

        # basic info for each Param subclass
        self.name: str = ''
        self.gx_var: str = ''
        self.gx_var_strings: set[str] = set()
        self.janis_var: str = ''
        self.galaxy_type: str = ''
        self.janis_type: str = ''
        self.default_value: str = ''
        self.help_text: str = ''
        self.cmd_references: list[VariableReference] = []

        # other bools
        self.is_optional: bool = False
        self.is_array: bool = False
        self.validated: bool = False

        # checks REWRITE
        self.has_command_ref: bool = False
        self.has_conditional_ref: bool = False
        # self.needed_user_input: bool = False 

        # linking to command string
        self.prefix: Optional[str] = None

        # galaxy stuff
        self.truths = ['true', 'True']


    def parse_common_features(self) -> None:
        self.set_name()
        self.set_help_text()
        self.set_gx_var()
        self.set_references()
        self.set_is_optional() # TODO potentially override func
        self.set_is_array() # TODO potentially override func
        self.remove_conditional_occurances()
        self.validate()
        

    def set_name(self) -> None:
        # name & prefix if argument 
        argument = get_attribute_value(self.node, 'argument')
        name = get_attribute_value(self.node, 'name')
        if argument != '':
            self.prefix = argument
            if name == '':
                self.name = argument.lstrip('-').replace('-', '_') 
            else:
                self.name = name
        else:
            self.name = name   


    def set_help_text(self) -> None:
        help_text = get_attribute_value(self.node, 'help')
        label = get_attribute_value(self.node, 'label')
       
        help_list = list(set([help_text, label]))
        help_list = [x for x in help_list if x != '']
        help_str = '. '.join(help_list)

        self.help_text = help_str

        """if help_text == '' and label != '':
            help_text = label
        self.help_text = help_text    """  


    def set_gx_var(self) -> None:
        tree_path = '.'.join(self.tree_path)
        if tree_path == '':
            self.update_gx_var(self.name)
        else:
            self.update_gx_var(tree_path + f'.{self.name}')


    def update_gx_var(self, new_var: str) -> None:
        self.gx_var = new_var


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
        

    def set_is_optional(self) -> None:
        if get_attribute_value(self.node, 'optional') in self.truths:
            self.is_optional = True

        if self.has_conditional_ref and not self.has_command_ref:
            self.is_optional = True
        

    def set_is_array(self) -> None:
        param_type = get_attribute_value(self.node, 'type')
        multiple = get_attribute_value(self.node, 'multiple')

        if param_type == 'data_collection':
            self.is_array = True
        elif multiple in self.truths:
            if param_type == 'data':
                self.is_array = True
        

    def remove_conditional_occurances(self) -> None:
        non_conditional_refs: list[VariableReference] = []
        for ref in self.cmd_references:
            if not ref.in_conditional:
                non_conditional_refs.append(ref)
        self.cmd_references = non_conditional_refs
    
       
    # occurs during postprocessing. called from ParamPostProcessor
    def user_select_prefix(self) -> str:
        # print basics
        print(f'\n--- prefix selection ---')
        print(f'var: {self.gx_var}')

        # print each candidate prefix
        for i, ref in enumerate(self.cmd_references):
            print(i, end=' ')
            print(ref.command_line)
        
        selected_elem = int(input('Selected command line reference [int]: '))
        prefix = self.cmd_references[selected_elem].prefix
        return prefix


    # the default class method
    def set_defaults(self) -> None:
        self.default_value = get_attribute_value(self.node, 'value')
        

    def validate(self) -> None:
        # more to come? 
        try:
            assert(self.name != '')
            assert(self.gx_var != None)
            assert(self.node != None)
            assert(self.has_command_ref)
            self.validated = True
        except AssertionError:
            pass


    def print_details(self):
        out_str = ''
        out_str += '\nparam --------------\n'

        out_str += f'gx_var: {self.gx_var}\n'
        out_str += f'prefix: {self.prefix}\n'
        out_str += f'datatype: {self.galaxy_type}\n'
        out_str += f'default_value: {self.default_value}\n'
        out_str += f'help_text: {self.help_text}\n'
        out_str += f'is_optional: {self.is_optional}\n'
        out_str += f'has_command_ref: {self.has_command_ref}\n'
        out_str += f'validated: {self.validated}\n'

        return out_str


    def __str__(self):
        temp_prefix = self.prefix or ''
        datatype = self.galaxy_type
        if type(self).__name__ == "BoolParam":
            datatype += f'({self.subtype})'
        return f'{self.gx_var[-49:]:50}{datatype[-24:]:25}{temp_prefix[-19:]:20}{self.has_command_ref:>10}'




class TextParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str], cmd_lines: list[str]):
        super().__init__(node, tree_path, cmd_lines)
        # type="color" is also TextParam
        self.galaxy_type: str = 'string' #?


    def parse(self) -> None:
        self.parse_common_features()
        self.set_defaults()



class IntParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str], cmd_lines: list[str]):
        super().__init__(node, tree_path, cmd_lines)
        self.galaxy_type: str = 'integer'


    def parse(self) -> None:
        self.parse_common_features()
        self.set_defaults()



class FloatParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str], cmd_lines: list[str]):
        super().__init__(node, tree_path, cmd_lines)
        self.galaxy_type: str = 'float'


    def parse(self) -> None:
        self.parse_common_features()
        self.set_defaults()



class DataParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str], cmd_lines: list[str]):
        super().__init__(node, tree_path, cmd_lines)


    def parse(self) -> None:
        self.parse_common_features()
        self.set_datatype()
        self.set_defaults()


    def set_datatype(self) -> None:
        temp_type = get_attribute_value(self.node, 'format')
        self.galaxy_type = consolidate_types(temp_type)


class BoolParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str], cmd_lines: list[str]):
        super().__init__(node, tree_path, cmd_lines)
        self.galaxy_type: str = 'boolean'
        self.subtype: str = ''


    def parse(self) -> None:
        self.validate_value_order()
        self.parse_common_features()
        self.set_bool_subtype()
        self.assert_structure()
        self.set_prefix()
        

    def validate_value_order(self) -> None:
        tv = get_attribute_value(self.node, 'truevalue')
        fv = get_attribute_value(self.node, 'falsevalue')
        if tv == '' and fv != '':
            self.node.attrib['truevalue'] = fv
            self.node.attrib['falsevalue'] = tv


    def set_bool_subtype(self) -> None:
        tv = get_attribute_value(self.node, 'truevalue')
        fv = get_attribute_value(self.node, 'falsevalue')
        if tv == '' and fv == '':
            self.subtype = 'true_bool'
        elif tv != '' and fv == '':
            self.subtype = 'flag_bool'


    def assert_structure(self) -> None:
        tv = get_attribute_value(self.node, 'truevalue')
        fv = get_attribute_value(self.node, 'falsevalue')
        if self.subtype == 'true_bool':
            assert(tv == '' and fv == '')
        elif self.subtype == 'flag_bool':
            assert(tv != '' and fv == '')


    def set_prefix(self):
        self.prefix = get_attribute_value(self.node, 'truevalue')
        pass



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
        param_type = "string"  # fallback

        # are the option values all a particular type?
        castable_type = cast_list(self.options)

        # do the option values all have a common extension? 
        common_extension = get_common_extension(self.options)
        
        # deciding what the type should be from our results
        if common_extension != '':
            param_type = common_extension
        elif castable_type != '':
            param_type = castable_type

        self.galaxy_type = consolidate_types(param_type)


    def add_options_to_helptext(self) -> None:
        options = ', '.join(self.options[:5])

        # trail off if more than 5 options...
        if len(self.options) > 5:
            options += '...' 

        self.help_text += f'  example values: {options}'


    def set_defaults(self) -> None:
        for child in self.node:
            if child.tag == 'option':
                if get_attribute_value(child, 'selected') in self.truths:
                    self.default_value = get_attribute_value(child, 'value')
                    break




class OutputParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str], cmd_lines: list[str]):
        super().__init__(node, tree_path, cmd_lines)


    def parse(self) -> None:
        self.parse_common_features()


    # override
    def set_help_text(self) -> None:
        label = get_attribute_value(self.node, 'label')
        if "${on_string}" in label:
            label = label.rsplit("${on_string}", 1)[1]
            label = label.strip(':')
            label = label.strip(' ')
            self.help_text = label



class DataCollectionParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str], cmd_lines: list[str]):
        super().__init__(node, tree_path, cmd_lines)
        self.collection_type: str = ''
        self.is_array: bool = True


    def parse(self) -> None:
        self.parse_common_features()
        self.parse_collection_type()
        self.set_datatype()
        self.set_defaults()


    def parse_collection_type(self) -> None:
        self.collection_type = get_attribute_value(self.node, 'collection_type')


    def set_datatype(self) -> None:
        temp_type = get_attribute_value(self.node, 'format')
        self.galaxy_type = consolidate_types(temp_type)



class HiddenParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str], cmd_lines: list[str]):
        super().__init__(node, tree_path, cmd_lines)

    
    def parse(self) -> None:
        pass