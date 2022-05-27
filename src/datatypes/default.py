

from datatypes.JanisDatatype import JanisDatatype

DEFAULT_DATATYPE = JanisDatatype(
    format='file',
    source='janis',
    classname='File',
    extensions=None,
    import_path='janis_core.types.common_data_types'
)

# DEFAULT_DATATYPE = JanisDatatype(
#     format='string',
#     source='janis',
#     classname='String',
#     extensions=None,
#     import_path='janis_core.types.common_data_types'
# )