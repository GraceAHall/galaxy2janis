


from .janis import JanisDatatype


def format_janis_str(datatypes: list[JanisDatatype], is_optional: bool, is_array: bool) -> str:
    # if len(datatypes) > 1:
    #     dtype = ', '.join([x.classname for x in datatypes])
    #     dtype = "UnionType(" + dtype + ")"
    # else:
    #     dtype = datatypes[0].classname
    
    dtype = datatypes[0].classname  # TODO hack to remove UnionType. 
    
    # not array not optional
    if not is_optional and not is_array:
        out_str = f'{dtype}'

    # array and not optional
    elif not is_optional and is_array:
        out_str = f'Array({dtype})'
    
    # not array and optional
    elif is_optional and not is_array:
        out_str = f'{dtype}(optional=True)'
    
    # array and optional
    elif is_optional and is_array:
        out_str = f'Array({dtype}(), optional=True)'

    return out_str