


import yaml
from paths import DATATYPES_YAML 
from typing import Optional
from .JanisDatatype import JanisDatatype



class DatatypeRegister:
    def __init__(self):
        self.dtype_map: dict[str, JanisDatatype] = self._load()

    def get(self, datatype: str) -> Optional[JanisDatatype]:
        if datatype in self.dtype_map:
            return self.dtype_map[datatype]

    def _load(self) -> dict[str, JanisDatatype]:
        """
        func loads the combined datatype yaml then converts it to dict with format as keys
        provides structue where we can search all the galaxy and janis types given what we see
        in galaxy 'format' attributes.
        """
        out: dict[str, JanisDatatype] = {}
        with open(DATATYPES_YAML, 'r') as fp:
            datatypes = yaml.safe_load(fp)
        for type_data in datatypes['types']:
            janistype = self._init_type(type_data)
            out[type_data['format']] = janistype
            out[type_data['classname']] = janistype # two keys per datatype
        return out

    def _init_type(self, dtype: dict[str, str]) -> JanisDatatype:
        return JanisDatatype(
            format=dtype['format'],
            source=dtype['source'],
            classname=dtype['classname'],
            extensions=dtype['extensions'],
            import_path=dtype['import_path']
        )


# SINGLETON
register = DatatypeRegister()
