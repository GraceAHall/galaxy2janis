
# pyright: basic

# Optional[str] means the type can be str or None. 

from xml.etree import ElementTree as et
from typing import Optional

from classes.logging.Logger import Logger


from utils.galaxy_utils import cast_list
from utils.etree_utils import get_attribute_value



class Param:
    def __init__(self, node: et.Element, tree_path: list[str]):
        # tree things
        self.node = node
        self.tree_path = tree_path

        # details to parse
        self.name: str = ''
        self.gx_var: str = ''
        self.galaxy_type: str = ''
        self.help_text: str = ''
        self.marked_optional: bool = False
        self.is_array: bool = False
        self.argument: Optional[str] = None

        # galaxy stuff
        self.truths = ['true', 'True']


    # override method
    def get_default_value(self) -> str:
        return ''


    def parse_common_features(self) -> None:
        self.set_name()
        self.set_gx_var()
        self.set_help_text()
        self.set_marked_optional() # TODO potentially override func
        self.set_is_array() # TODO potentially override func


    def set_name(self) -> None:
        # name & prefix if argument 
        argument = get_attribute_value(self.node, 'argument')
        name = get_attribute_value(self.node, 'name')
        if argument != '':
            self.argument = argument
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


    def set_gx_var(self) -> None:
        tree_path = '.'.join(self.tree_path)
        if tree_path == '':
            self.update_gx_var(self.name)
        else:
            self.update_gx_var(tree_path + f'.{self.name}')


    def update_gx_var(self, new_var: str) -> None:
        self.gx_var = new_var


    def set_marked_optional(self) -> None:
        if get_attribute_value(self.node, 'optional') in self.truths:
            self.marked_optional = True
        

    def set_is_array(self) -> None:
        param_type = get_attribute_value(self.node, 'type')
        multiple = get_attribute_value(self.node, 'multiple')

        if param_type == 'data_collection':
            self.is_array = True
        elif multiple in self.truths:
            if param_type == 'data':
                self.is_array = True      
    

    def print_details(self):
        out_str = ''
        out_str += '\nparam --------------\n'

        out_str += f'gx_var: {self.gx_var}\n'
        out_str += f'prefix: {self.argument}\n'
        out_str += f'datatype: {self.galaxy_type}\n'
        out_str += f'default_value: {self.default_value}\n'
        out_str += f'help_text: {self.help_text}\n'
        out_str += f'marked_optional: {self.marked_optional}\n'
        
        return out_str


    def __str__(self):
        temp_prefix = self.argument or ''
        datatype = self.galaxy_type
        if isinstance(self, BoolParam):
            datatype = 'boolean'
        return f'{self.gx_var[-49:]:50}{datatype[-14:]:15}'





###### CHILD CLASSES START ######


class TextParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str]):
        super().__init__(node, tree_path)
        # type="color" is also TextParam
        self.galaxy_type: str = 'string' 
        self.value = get_attribute_value(node, 'value')
        self.parse_common_features()


    def get_default_value(self) -> str:
        return self.value



class IntParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str]):
        super().__init__(node, tree_path)
        self.galaxy_type: str = 'integer'
        self.value = get_attribute_value(node, 'value')
        self.parse_common_features()

    
    def get_default_value(self) -> str:
        return self.value



class FloatParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str]):
        super().__init__(node, tree_path)
        self.galaxy_type: str = 'float'
        self.value = get_attribute_value(node, 'value')
        self.parse_common_features()


    def get_default_value(self) -> str:
        return self.value



class DataParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str]):
        super().__init__(node, tree_path)
        self.galaxy_type = get_attribute_value(self.node, 'format')
        self.parse_common_features()


    def get_default_value(self) -> str:
        return ''



class BoolParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str]):
        super().__init__(node, tree_path)
        self.galaxy_type: str = 'boolean'
        self.truevalue: str = get_attribute_value(node, 'truevalue')
        self.falsevalue: str = get_attribute_value(node, 'falsevalue')
        self.parse_common_features()


    def get_default_value(self) -> str:
        if self.truevalue != '':
            return self.truevalue
        return self.falsevalue


    def values_are_flags(self) -> bool:
        # get values and remove any key/val pairs
        values = [self.truevalue, self.falsevalue]
        values = [v for v in values if '=' not in v and ' ' not in v]
        
        # none were keyvals
        if len(values) == 2:
            num_blanks = len([v for v in values if v == ''])
            num_opts = len([v for v in values if v.startswith('-')])
            
            # one is flag, other is empty
            if num_blanks == 1 and num_opts == 1:
                return True

            # both are flags but different
            if num_opts == 2 and values[0] != values[1]:
                return True

        return False




class SelectParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str], logger: Logger):
        super().__init__(node, tree_path)
        self.options: list[str] = self.get_param_options(logger)
        self.opts_from_data_table: bool = False
        self.galaxy_type: str = self.get_datatype()
        self.parse_common_features()
        self.add_options_to_helptext()


    def get_default_value(self) -> str:
        if len(self.options) > 0:
            return self.options[0]
        return ''


    def get_param_options(self, logger: Logger) -> list[str]:
        # get options from child option nodes
        option_values = []
        for child in self.node:
            if child.tag == 'option':
                optval = get_attribute_value(child, 'value')

                # if 'selected=True', put this option at the top of list
                if get_attribute_value(child, 'selected') in self.truths:
                    option_values = [optval] + option_values
                else:
                    option_values.append(optval)  # type: ignore
                
            elif child.tag == 'options':
                # 135 iuc tools. This is now supported!
                if 'from_data_table' in child.attrib:
                    self.opts_from_data_table = True
                    
                # error messages for unsupported features
                # 2 iuc tools
                if 'from_dataset' in child.attrib:
                    logger.log(2, 'options from_dataset encountered')
                # 0 iuc tools
                if 'from_file' in child.attrib:
                    logger.log(2, 'options from_file encountered')
                # 0 iuc tools
                if 'from_parameter' in child.attrib:
                    logger.log(2, 'options from_parameter encountered')
                # 3 iuc tools
                if 'options_filter_attribute' in child.attrib:
                    logger.log(2, 'options options_filter_attribute encountered')
                # 0 iuc tools
                if 'transform_lines' in child.attrib:
                    logger.log(2, 'options transform_lines encountered')
                # 0 iuc tools
                if 'startswith' in child.attrib:
                    logger.log(2, 'options startswith encountered')                

        # option list is same order as in galaxy except 'selected' option is 1st
        return option_values
        

    def get_datatype(self) -> str:
        """
        infers select param type. 
        Uses the different values in the option elems.
        param options are already stored in param.options
        """
        fallback = "string"  # fallback

        if self.opts_from_data_table:
            return 'file'
         
        # are the option values all a particular type?
        castable_type = cast_list(self.options)
        if castable_type != '':
            return castable_type
        
        return fallback   


    def add_options_to_helptext(self) -> None:
        """
        adds non flag looking options to helptext
        i hate how this is written for some reason
        """
        options = [opt for opt in self.options if not opt.startswith('-')]
        
        # trail off if more than 5 options...
        should_add_dots = False
        if len(options) > 5:
            should_add_dots = True
        
        options = ', '.join(options[:5])

        if should_add_dots:
            options += '...' 

        if len(options) > 0:
            self.help_text += f'  example values: {options}'

    
    def values_are_flags(self) -> bool:
        if len(self.options) == 0:
            return False

        # get blanks or opt looking items
        opts = [o for o in self.options if o.startswith('-') or o == '']

        # remove kv pairs
        opts = [o for o in opts if '=' not in o and ' ' not in o]

        # all thats left are flags and blanks. 
        # ensure there is at least 2 nonblanks
        nonblanks = [o for o in opts if o != '']
        if len(nonblanks) >= 2:
            # if this is same length as original list (self.options), theyre probably individual flags
            if len(opts) == len(self.options):
                return True
        
        return False
        

class DataCollectionParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str]):
        super().__init__(node, tree_path)
        self.collection_type = get_attribute_value(self.node, 'collection_type')
        self.galaxy_type = get_attribute_value(self.node, 'format')
        self.parse_common_features()
        self.is_array: bool = True


    def get_default_value(self) -> str:
        return ''



class HiddenParam(Param):
    def __init__(self, node: et.Element, tree_path: list[str]):
        super().__init__(node, tree_path)
        self.parse_common_features()
        self.value = get_attribute_value(node, 'value')

    