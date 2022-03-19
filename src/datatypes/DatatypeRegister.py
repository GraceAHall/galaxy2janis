


from dataclasses import dataclass
from typing import Optional
import yaml

from .JanisDatatype import JanisDatatype


@dataclass
class DatatypeDetails:
    datatypes: list[JanisDatatype]
    is_optional: bool
    is_array: bool
    is_stdout: bool


class DatatypeRegister:
    def __init__(self):
        self.datatype_definitions_path = 'datatypes/gxformat_combined_types.yaml'
        self.dtype_map: dict[str, JanisDatatype] = {}
        self.load_yaml_to_dtype_map()
        #self.ext_to_raw_map = self.index_by_ext(self.format_datatype_map)

    def get(self, datatype: str) -> Optional[JanisDatatype]:
        if datatype in self.dtype_map:
            return self.dtype_map[datatype]

    def load_yaml_to_dtype_map(self) -> None:
        """
        func loads the combined datatype yaml then converts it to dict with format as keys
        provides structue where we can search all the galaxy and janis types given what we see
        in galaxy 'format' attributes.
        """
        with open(self.datatype_definitions_path, 'r') as fp:
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






# string_t = JanisDatatype(
#     format='string',
#     source='janis',
#     classname='String',
#     extensions=None,
#     import_path='janis_core.types.common_data_types' 
# )
# integer_t = JanisDatatype(
#     format='integer',
#     source='janis',
#     classname='Int',
#     extensions=None,
#     import_path='janis_core.types.common_data_types'
# )
# float_t = JanisDatatype(
#     format='float',
#     source='janis',
#     classname='Float',
#     extensions=None,
#     import_path='janis_core.types.common_data_types'
# )
# file_t = JanisDatatype(
#     format='file',
#     source='janis',
#     classname='File',
#     extensions=None,
#     import_path='janis_core.types.common_data_types'
# )

    # def index_by_ext(self, format_datatype_map: dict[str, dict[str, str]]) -> dict[str, str]:
    #     """
    #     maps ext -> list of jtypes (janis / galaxy) 
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
