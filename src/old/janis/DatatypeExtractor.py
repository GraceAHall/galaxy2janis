




import yaml
from typing import Optional, Union

from galaxy.tool_util.parser.output_collection_def import FilePatternDatasetCollectionDescription
from galaxy.tools.parameters.basic import ToolParameter
from galaxy.tool_util.parser.output_objects import ToolOutput

from galaxy_tool.param.ParamRegister import ParamRegister
from galaxy_tool.param.OutputRegister import OutputRegister
from command.CommandComponents import Positional, Flag, Option, Output
from command.Command import TokenType
from logger.Logger import Logger

from utils.galaxy_utils import (
    get_param_formats, 
    get_output_formats, 
    is_tool_parameter, 
    is_tool_output
)

CommandComponent = Union[Positional, Flag, Option]


class DatatypeExtractor:
    def __init__(self, param_register: ParamRegister, out_register: OutputRegister, logger: Logger):
        self.logger = logger
        self.param_register = param_register
        self.out_register = out_register
        self.init_datastructures()
        
        # fallback types
        self.string_t = {
            'format': 'string',
            'source': 'janis',
            'classname': 'String',
            'extensions': None,
            'import_path': 'janis_core.types.common_data_types'
        } 
        self.integer_t = {
            'format': 'integer',
            'source': 'janis',
            'classname': 'Int',
            'extensions': None,
            'import_path': 'janis_core.types.common_data_types'
        }
        self.float_t = {
            'format': 'float',
            'source': 'janis',
            'classname': 'Float',
            'extensions': None,
            'import_path': 'janis_core.types.common_data_types'
        }
        self.file_t = {
            'format': 'file',
            'source': 'janis',
            'classname': 'File',
            'extensions': None,
            'import_path': 'janis_core.types.common_data_types'
        }


    def init_datastructures(self) -> None:
        self.format_datatype_map = self.load_yaml('src/data/gxformat_combined_types.yaml')
        self.ext_to_format_map = self.index_by_ext(self.format_datatype_map)
    

    def load_yaml(self, filepath: str) -> dict[str, dict[str, str]]:
        """
        func loads the combined datatype yaml then converts it to dict with format as keys
        provides structue where we can search all the galaxy and janis types given what we see
        in galaxy 'format' attributes.
        """
        with open(filepath, 'r') as fp:
            datatypes = yaml.safe_load(fp)
        
        format_datatype_map = {}

        for dtype in datatypes['types']:
            # add new elem if not exists
            if dtype['format'] not in format_datatype_map:
                format_datatype_map[dtype['format']] = []
            
            # add this type
            format_datatype_map[dtype['format']].append(dtype)

        return format_datatype_map


    def index_by_ext(self, format_datatype_map: dict[str, dict[str, str]]) -> dict[str, str]:
        """
        maps ext -> list of datatypes (janis / galaxy) 
        this way can look up a file extension, and get the gxformats that use that type
        can then use self.format_datatype_map to get the actual janis and galaxy type info 
        """
        ext_format_map = {}
        for gxformat, dtype_list in format_datatype_map.items():
            # get all exts from galaxy + janis types of that gxformat
            exts = set()
            for dtype in dtype_list:
                if dtype['extensions'] is not None:
                    dtype_exts = dtype['extensions'].split(',')
                    exts.update(dtype_exts)
            
            # for each ext, add as key to ext_format_map or append datatype to that key
            for ext in list(exts):
                # make entry if not exists
                if ext not in ext_format_map:
                    ext_format_map[ext] = []
                # append gxformat
                ext_format_map[ext].append(gxformat)

        return ext_format_map


    def extract(self, incoming: Union[CommandComponent, Output]) -> list[dict]:
        """
        delegates whether the incoming is a CommandComponent or ToolOutput. 
        datatype extraction logic is different for these two classes. 
        """
        if isinstance(incoming, Output):
            return self.extract_from_output(incoming)
        else:
            return self.extract_from_component(incoming)


    def extract_from_output(self, output: Output) -> list[dict]:
        types = []

        galaxy_formats = get_output_formats(output.galaxy_object, self.param_register)
        for gxformat in galaxy_formats:
            types += self.cast_gxformat_to_datatypes(gxformat)

        # fallback 
        if len(types) == 0:
            types.append(self.file_t)

        return types
                

    def extract_from_component(self, component: CommandComponent) -> list[dict]:
        """
        delegates what method to use for datatype inference.
        """
        # galaxy 
        gxobj = component.galaxy_object
        if gxobj:
            if is_tool_parameter(gxobj):
                return self.extract_types_from_galaxy_param(component)
            elif is_tool_output(gxobj):
                return self.extract_types_from_galaxy_output(gxobj)
        
        # int or float
        numbers_set = set([TokenType.RAW_NUM, TokenType.QUOTED_NUM])
        component_set = component.get_token_types()
        if component_set.issubset(numbers_set):
            #types = self.extract_types_from_numeric(component)
            #return types
            return self.extract_types_from_numeric(component)

        # from string
        elif TokenType.RAW_STRING in component_set or TokenType.QUOTED_STRING in component_set:
            #types = self.extract_types_from_strings(component)
            #return types
            return self.extract_types_from_strings(component)

        # fallback
        return [self.string_t]


    def extract_types_from_galaxy_param(self, component: CommandComponent) -> list[dict]:
        gxobj = component.galaxy_object
        if gxobj.type == 'integer':
            return [self.integer_t]
        elif gxobj.type == 'float':
            return [self.float_t]
        elif gxobj.type in ['text', 'color']:
            return [self.string_t]
        elif gxobj.type in ['data', 'data_collection']:
            return self.extract_types_from_gx_format(gxobj)
        elif gxobj.type == 'select':
            return self.extract_types_from_gx_select(component)

    
    def extract_types_from_galaxy_output(self, gxobj: ToolOutput) -> list[dict]:
        types = []
        
        if gxobj:   
            for gxformat in get_output_formats(gxobj, self.param_register):
                types += self.cast_gxformat_to_datatypes(gxformat)

        if len(types) == 0:
            types.append(self.file_t)

        return types


    def extract_types_from_numeric(self, component: CommandComponent) -> list[dict]:
        """
        all occurances of the CommandComponent were numeric.
        if any of the sources are floats, return float, else int
        """
        for value in component.get_token_values(as_list=True):
            if '.' in value:
                return [self.float_t]

        return [self.integer_t]


    def extract_types_from_strings(self, component: CommandComponent) -> list[dict]:
        out_types = []

        # guess type from file extensions if present
        for value in component.get_token_values(as_list=True):
            ext_datatype = self.get_extension_datatype(value)
            if ext_datatype is not None:
                out_types.append(ext_datatype)
        
        # extensions didn't help, return fallback
        if len(out_types) == 0:
            out_types.append(self.string_t)

        return out_types


    def get_extension_datatype(self, the_string: str) -> Optional[dict]:
        components = the_string.split('.')
        components = [c for c in components if c != '']

        # extract gxformats which we are aware of through extensions
        # this is iterative and will prioritise the longest extension match
        gxformat = ''
        if len(components) > 1:
            for i in range(1, len(components)):
                ext = '.'.join(components[i:])
                if ext in self.ext_to_format_map:
                    gxformat = self.ext_to_format_map[ext]
                    break

        # for the final chosen gxformat, convert to janis datatype if exists
        if gxformat != '':
            dtype = self.cast_gxformat_to_datatypes(gxformat)
            if dtype is not None:
                return dtype

        return None


    # now the datastructures are initialised, here are some methods
    # to access types given gxformat or extension
    def extract_types_from_gx_format(self, gxobj: ToolParameter) -> list[dict[str, str]]:
        types = []
        
        if gxobj is not None:   
            for gxformat in get_param_formats(gxobj):
                types += self.cast_gxformat_to_datatypes(gxformat)

        if len(types) == 0:
            types.append(self.file_t)

        return types


    # now the datastructures are initialised, here are some methods
    # to access types given gxformat or extension
    def extract_types_from_gx_select(self, component: CommandComponent) -> list[dict[str, str]]:       
        if component.galaxy_object is not None and component.galaxy_object.type == 'select':
            component_tokens = component.get_galaxy_options(as_tokens=True)
            # all tokens are numeric
            out = [t.type in [TokenType.RAW_NUM, TokenType.QUOTED_NUM] for t in component_tokens]
            if all([t.type in [TokenType.RAW_NUM, TokenType.QUOTED_NUM] for t in component_tokens]):
                # at least 1 is a float
                if any(['.' in t.text for t in component_tokens]):
                    return [self.float_t]
                else:
                    return [self.int_t]

        # potentially add type sniffing from common extension
        
        # fallback
        return [self.string_t]

    
    def cast_gxformat_to_datatypes(self, gxformat: str) -> list[dict[str, str]]:
        # get all the datatypes which map to the gxformat
        if gxformat in self.format_datatype_map:
            formatted_types = self.format_datatype_map[gxformat]

            if len(formatted_types) > 1:            
                for dtype in formatted_types:
                    if dtype['source'] == 'janis':
                        return [dtype]
            elif len(formatted_types) == 1:
                return [formatted_types[0]]

        return []


    def assert_has_datatype(self, obj):
        # TODO
        pass


    


"""
  
  
def get_best_gxformat(self, ext: str, gxformat_list: list[str]) -> str:
    \"""
    gxformat_list will always be passed with 1+ items
    \"""
    gxformat_distances = []

    for gxformat in gxformat_list:
        dist = self.levenshtein(ext, gxformat)
        gxformat_distances.append((gxformat, dist))
    
    gxformat_distances.sort(key=lambda x: x[1])
    return gxformat_distances[0]


# this is adapted from:
# https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python
@staticmethod
def levenshtein(s1, s2):
    if len(s1) < len(s2):
        s1, s2 = s2, s1

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def infer_types_from_gx(self, the_token: Token) -> list[dict[str, str]]:
        \"""
        for gx params or gx outputs
        gx params and outputs already have type annotation
        extracted from the xml
        always returns list, but list may have zero items
        \"""
        fallback_datatypes = self.file_t

        if the_token.type == TokenType.GX_PARAM:
            varname, param = self.tool.param_register.get(the_token.gx_ref)
            gxformat_list = param.galaxy_type.split(',')

        elif the_token.type == TokenType.GX_OUT:
            output_var, output = self.tool.out_register.get(the_token.gx_ref)
            gxformat_list = output.galaxy_type.split(',')

        if len(gxformat_list) == 0:
            return fallback_datatypes
        
        datatypes = []
        for gxformat in gxformat_list:
            dtype = self.extract_types_from_gx_format(gxformat)
            if dtype is not None:
                datatypes.append(dtype)
        
        if len(datatypes) == 0:
            return fallback_datatypes

        return datatypes


    def infer_types_from_ext(self, the_string: str) -> list[dict[str, str]]:
        \"""
        2 steps: ext -> gxformat, gxformat -> dtype
        returns the datatypes which use the identified extension
        the best extension is identified then translated to gxformat
        the longest extension is used
        ie for input.fq.gz, .fq.gz is set as best extension rather than .gz
        \"""
        fallback_datatypes = self.string_t
            
        gxformat = ''
        components = the_string.split('.')
        components = [c for c in components if c != '']

        if len(components) > 1:
            for i in range(1, len(components)):
                ext = '.'.join(components[i:])
                if ext in self.ext_to_format_map:
                    gxformat = self.ext_to_format_map[ext]
                    break

        if gxformat != '':
            dtype = self.extract_types_from_gx_format(gxformat)
            if dtype is not None:
                return [dtype]

        return fallback_datatypes


    def select_datatypes_source(self, source_datatypes) -> list[str]:  # type: ignore
        \"""
        flags or option can have multiple references in the command string
        and therefore be set from multiple tokens
        some tokens (ie GX_PARAM or GX_OUT) are more informative of the real type(s)
        this func selects the best source to annotate types from
        \"""

        from_galaxy = []
        for token_type, datatypes in source_datatypes:
            if token_type in [TokenType.GX_PARAM, TokenType.GX_OUT] and len(datatypes) > 0:
                from_galaxy.append(datatypes)
        
        from_numeric = [dt for tt, dt in source_datatypes if tt in [TokenType.RAW_NUM, TokenType.QUOTED_NUM]]    
        from_string = [dt for tt, dt in source_datatypes if tt in [TokenType.RAW_STRING, TokenType.QUOTED_STRING]]    

        # galaxy is best 
        if len(from_galaxy) > 0:
            return from_galaxy[0] # hopefully just 1 galaxy obj ref

        # then numeric
        elif len(from_numeric) > 0:
            return from_numeric[0]
        
        # then string
        if len(from_string) > 0:
            return from_string[0]
        
        # don't care about the rest. equal importance. 
        return source_datatypes[0][1]


    def get_output_datatype(self, the_output: ToolOutput) -> list[str]:
        fallback_datatypes = self.file_t

        datatypes = []

        # try from galaxy_type first
        if the_output.galaxy_type != '':    
            gxformat_list = the_output.galaxy_type.split(',')
            for gxformat in gxformat_list:
                dtype = self.extract_types_from_gx_format(gxformat)
                if dtype is not None:
                    datatypes.append(dtype)

        # then from the extension on the selector contents
        if len(datatypes) == 0:
            datatypes = self.infer_types_from_ext(the_output.selector_contents)
            datatypes = [d for d in datatypes if d['classname'] != 'String']
        
        if len(datatypes) >= 1:
            return datatypes

        # fallback   
        return fallback_datatypes     



    
"""