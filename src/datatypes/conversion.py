




from datatypes.DatatypeRegister import DatatypeRegister
from datatypes.JanisDatatype import JanisDatatype


file_t = JanisDatatype(
    format='file',
    source='janis',
    classname='File',
    extensions=None,
    import_path='janis_core.types.common_data_types'
)

def cast_gx_to_janis(gxtype: str) -> JanisDatatype:
    reg = DatatypeRegister()
    jtype = reg.get(gxtype)
    if jtype is None:
        jtype = file_t # fallback
    return jtype

