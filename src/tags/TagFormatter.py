

import tags.filters as filters



class TagFormatter:
    """formats a string and some optional extra details into a base tag"""

    def format(self, entity_info: dict[str, str]) -> str:
        tag = entity_info['name']
        tag = filters.format_capitalisation(tag)
        tag = filters.replace_non_alphanumeric(tag)
        tag = filters.handle_prohibited_key(tag)
        tag = filters.handle_short_tag(tag, entity_info)
        tag = filters.encode(tag)
        return tag


    """


filters_map = {
    'tool': [
        filters.format_capitalisation,
    ],
    'step': [],
    'runtime_value': []
}

    def format(self, tag_type: str, the_string: str, datatype: Optional[str]=None) -> str:
        datatype = datatype.lower() if datatype else None
        filters_to_apply = filters_map[tag_type]
        for filt in filters_to_apply:
            the_string = filt(the_string)
        return the_string


    
class TagFormatter(ABC):
    def __init__(self, the_string: str):
        self.the_string = the_string

    @abstractmethod
    def format(self) -> str:
        ...


class ToolTagFormatter(TagFormatter):
    def __init__(self, the_string: str, datatype: Optional[str]=None):
        self.the_string = the_string
        self.datatype = datatype
        self.filters = [
            
        ]

    def format(self) -> str:
        raise NotImplementedError()







    """

    
    



        