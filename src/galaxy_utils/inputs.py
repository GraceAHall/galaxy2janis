


from typing import Optional, Any

from galaxy.tool_util.parser.output_collection_def import FilePatternDatasetCollectionDescription
from galaxy.tool_util.parser.output_objects import ToolOutput
from galaxy.tools.parameters.basic import ToolParameter
from galaxy.tools import Tool as GalaxyTool

from galaxy.tools.parameters.grouping import Conditional, ConditionalWhen, Section, Repeat

from copy import copy


XmlNode = ToolParameter | Conditional | ConditionalWhen | Section | Repeat

class ParamFlattener:
    def __init__(self, inputs: dict[str, Any]):
        self.inputs = inputs
        self.flat_params: list[ToolParameter] = []   

    def flatten(self) -> list[ToolParameter]:
        for node in self.inputs.values():
            self.explore_node(node, [])
        return self.flat_params

    def explore_node(self, node: XmlNode, heirarchy: list[str]) -> None:
        heirarchy = copy(heirarchy)
        match node:
            case ToolParameter():
                node.name = f'{".".join(heirarchy)}.{node.name}'
                self.flat_params.append(node)

            case Conditional():
                heirarchy.append(node.name)
                for child in node.cases:
                    self.explore_node(child, heirarchy)

            case ConditionalWhen():
                for child in node.inputs.values():
                    self.explore_node(child, heirarchy)

            case Repeat() | Section():
                heirarchy.append(node.name)
                for child in node.inputs.values():
                    self.explore_node(child, heirarchy)

            case _:
                raise NotImplementedError
            

def get_flattened_params(toolrep: GalaxyTool) -> list[ToolParameter]:
    pf = ParamFlattener(toolrep.inputs)
    return pf.flatten()




#### OLD


def is_tool_parameter(gxobj: Any) -> bool:
    if isinstance(gxobj, ToolParameter):
        return True
    elif issubclass(type(gxobj), ToolParameter):
        return True
    return False


def get_param_formats(param: ToolParameter) -> list[str]:
    if param.formats:
        return [f.file_ext for f in param.formats]
    
    return []


def get_param_values(param: ToolParameter) -> list[str]:
    if param.type in ['select', 'boolean']:
        return get_param_options(param)
    
    elif param.type not in ['data', 'data_collection']:
        if param.value:
            return [param.value]
        
    return []

       
def get_param_options(param: ToolParameter) -> list[str]:
    """this works for select AND boolean params"""
    return param.legal_values


def get_param_default_value(param: ToolParameter) -> Optional[str]:
    if hasattr(param, 'value') and param.value is not None:
        return param.value
    
    elif param.type in ['select', 'boolean']:
        return get_param_primary_option(param)

    elif param.type in ['data', 'data_collection']:
        if len(param.formats) > 0:
            ext = param.formats[0].file_ext
            return param.name + '.' + ext

    elif param.type in ['integer', 'float']:
        if param.min:
            return param.min
        elif param.max:
            return param.max

    return None


def get_param_primary_option(param: ToolParameter) -> Optional[str]:
    # select params
    if param.type == 'select':
        for opt in param.static_options:
            if opt[2] is True:
                return opt[1]
        return param.static_options[0][1]
    
    # boolean params
    elif param.type == 'boolean':
        if hasattr(param, 'checked'):
            if param.checked == 'false':
                return param.falsevalue
            return param.truevalue
        
        else:
            if param.truevalue and param.truevalue != '':
                return param.falsevalue
            return param.truevalue

    return None


def get_output_dataset_collector(output: ToolOutput) -> Optional[FilePatternDatasetCollectionDescription]:
    if hasattr(output, 'dataset_collector_descriptions'):
        if output.dataset_collector_descriptions:
            return output.dataset_collector_descriptions[0]
    return None


def param_is_optional(param: ToolParameter) -> bool:
    # optionality explicitly set as true in param
    if param.optional:
        return True
    # param values include a blank string
    if '' in get_param_values(param):
        return True
    
    return False


def param_is_array(param: ToolParameter) -> bool:
    if param.type == 'data_collection':
        return True
    elif param.type == 'data' and param.multiple:
        return True
        
    return False