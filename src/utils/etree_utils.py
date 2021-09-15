
#pyright: strict

# libraries
from xml.etree import ElementTree as et

# local modules


# TODO add tests for each of these!


# ---- converting between elem types ---- #

def convert_bool_to_select_elem(node: et.Element) -> et.Element:
    # convert param attributes
    attributes = {
        'type': 'select',
        'name': get_attribute_value(node, 'name'),
        'label': get_attribute_value(node, 'label'),
        'help': get_attribute_value(node, 'help'),
        'multiple': 'False'
    }
    parent = et.Element('param', attributes)

    # create child option for each bool value
    tv = get_attribute_value(node, 'truevalue')
    fv = get_attribute_value(node, 'falsevalue')

    for val in [tv, fv]:
        attributes = {'value': val}
        child = et.Element('option', attributes)
        parent.append(child)
    
    return parent


def convert_select_to_bool_elems(node: et.Element) -> list[et.Element]:
    # TODO change to dict only later
    out_elems = []
    
    options = get_select_options(node)
    for opt in options:
        bool_elem = create_bool_elem(node, opt['value'], opt['text'])
        out_elems.append(bool_elem)

    return out_elems



# ---- creating et.Elements ---- #

def create_bool_elem(node: et.Element, val: str, text: str) -> et.Element:
    # bool elem
    attributes = {
        'name': get_attribute_value(node, 'name'),
        'argument': get_attribute_value(node, 'argument'),
        'label': text,
        'type': 'boolean',
        'checked': 'False',
        'truevalue': val,
        'falsevalue': ''
    }
    node = et.Element('param', attributes)
    return node



# ---- reading node contents ---- #

def get_attribute_value(node: et.Element, attribute: str) -> str:
        '''
        accepts node, returns attribute value or "" 
        '''
        for key, val in node.attrib.items():
            if key == attribute:
                return val
        return ""


def get_select_options(node: et.Element) -> list[dict[str, str]]:
    # TODO convert to dict only 
    options = []

    for child in node:
        if child.tag == 'option':
            opt = {'value': child.attrib['value'], 'text': child.text or ''}
            options.append(opt)
    
    return options


def get_param_name(node: et.Element) -> str:
    name = get_attribute_value(node, 'name')
    if name == '':
        name = get_attribute_value(node, 'argument').lstrip('-').replace('-', '_')
    assert(name != '') 
    return name