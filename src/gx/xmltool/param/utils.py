




from gx.xmltool.param.InputParam import SelectParam


def select_is_bool(gxparam: SelectParam) -> bool:
    values = gxparam.get_all_values(nonempty=True)
    if len(values) == 1:
        if values[0].startswith('-'):
            return True
    return False