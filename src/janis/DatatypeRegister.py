



from dataclasses import dataclass
from typing import Optional
from command.components.CommandComponent import CommandComponent
from runtime.settings import ExecutionSettings
import yaml

@dataclass
class JanisDatatype:
    format: str
    source: str
    classname: str
    extensions: Optional[str]
    import_path: str

string_t = JanisDatatype(
    format='string',
    source='janis',
    classname='String',
    extensions=None,
    import_path='janis_core.types.common_data_types' 
)
integer_t = JanisDatatype(
    format='integer',
    source='janis',
    classname='Int',
    extensions=None,
    import_path='janis_core.types.common_data_types'
)
float_t = JanisDatatype(
    format='float',
    source='janis',
    classname='Float',
    extensions=None,
    import_path='janis_core.types.common_data_types'
)
file_t = JanisDatatype(
    format='file',
    source='janis',
    classname='File',
    extensions=None,
    import_path='janis_core.types.common_data_types'
)

class DatatypeRegister:
    def __init__(self, esettings: ExecutionSettings):
        self.dtype_map: dict[str, JanisDatatype] = {}
        self.load_yaml_to_dtype_map(esettings.get_datatype_definitions_path())
        #self.ext_to_raw_map = self.index_by_ext(self.format_datatype_map)

    def load_yaml_to_dtype_map(self, filepath: str) -> None:
        """
        func loads the combined datatype yaml then converts it to dict with format as keys
        provides structue where we can search all the galaxy and janis types given what we see
        in galaxy 'format' attributes.
        """
        with open(filepath, 'r') as fp:
            datatypes = yaml.safe_load(fp)
        for dtype in datatypes['types']:
            self.update_dtype_map(dtype)

    def update_dtype_map(self, dtype: dict[str, str]) -> None:
        # add new elem if not exists
        fmt: str = dtype['format']
        # add this type
        new_type = JanisDatatype(
            format=dtype['format'],
            source=dtype['source'],
            classname=dtype['classname'],
            extensions=dtype['extensions'],
            import_path=dtype['import_path']
        )
        self.dtype_map[fmt] = new_type
        self.dtype_map[dtype['classname']] = new_type # two keys per datatype

    def get(self, datatypes: list[str]) -> list[JanisDatatype]:
        out: list[JanisDatatype] = [] 
        for dtype in datatypes:
            if dtype in self.dtype_map:
                out.append(self.dtype_map[dtype])
        return out

    def to_janis_def_string(self, component: CommandComponent) -> str:
        """
        turns a component and datatype dict into a formatted string for janis definition.
        the component is used to help detect array / optionality. 
            String
            String(optional=True)
            Array(String(), optional=True)
            etc
        """
        datatypes = component.get_datatype()
        datatypes = self.get(datatypes)
        if len(datatypes) > 1:
            dtype = ', '.join([x.classname for x in datatypes])
            dtype = "UnionType(" + dtype + ")"
        else:
            dtype = datatypes[0].classname
        
        # not array not optional
        if not component.is_optional() and not component.is_array():
            out_str = f'{dtype}'

        # array and not optional
        elif not component.is_optional() and component.is_array():
            out_str = f'Array({dtype})'
        
        # not array and optional
        elif component.is_optional() and not component.is_array():
            out_str = f'{dtype}(optional=True)'
        
        # array and optional
        elif component.is_optional() and component.is_array():
            out_str = f'Array({dtype}(), optional=True)'

        return out_str





    # def index_by_ext(self, format_datatype_map: dict[str, dict[str, str]]) -> dict[str, str]:
    #     """
    #     maps ext -> list of datatypes (janis / galaxy) 
    #     this way can look up a file extension, and get the gxformats that use that type
    #     can then use self.format_datatype_map to get the actual janis and galaxy type info 
    #     """
    #     ext_format_map = {}
    #     for gxformat, dtype_list in format_datatype_map.items():
    #         # get all exts from galaxy + janis types of that gxformat
    #         exts = set()
    #         for dtype in dtype_list:
    #             if dtype['extensions'] is not None:
    #                 dtype_exts = dtype['extensions'].split(',')
    #                 exts.update(dtype_exts)
            
    #         # for each ext, add as key to ext_format_map or append datatype to that key
    #         for ext in list(exts):
    #             # make entry if not exists
    #             if ext not in ext_format_map:
    #                 ext_format_map[ext] = []
    #             # append gxformat
    #             ext_format_map[ext].append(gxformat)

    #     return ext_format_map
