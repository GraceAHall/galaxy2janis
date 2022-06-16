

# import tags.formatters as formatters



# class TagFormatter:
#     """formats a string and some optional extra details into a base tag"""

#     def format(self, tag_type: str, entity: TaggableEntity) -> str:
#         tag = formatters.format_capitalisation(tag)
#         tag = formatters.replace_non_alphanumeric(tag)
#         tag = formatters.handle_prohibited_key(tag)
#         tag = formatters.handle_short_tag(tag, entity_info)
#         tag = formatters.encode(tag)
#         return tag


#     """


# filters_map = {
#     'tool': [
#         filters.format_capitalisation,
#     ],
#     'step': [],
#     'runtime_value': []
# }

#     def format(self, tag_type: str, the_string: str, datatype: Optional[str]=None) -> str:
#         datatype = datatype.lower() if datatype else None
#         filters_to_apply = filters_map[tag_type]
#         for filt in filters_to_apply:
#             the_string = filt(the_string)
#         return the_string


    
# class TagFormatter(ABC):
#     def __init__(self, the_string: str):
#         self.the_string = the_string

#     @abstractmethod
#     def format(self) -> str:
#         ...


# class ToolTagFormatter(TagFormatter):
#     def __init__(self, the_string: str, datatype: Optional[str]=None):
#         self.the_string = the_string
#         self.datatype = datatype
#         self.filters = [
            
#         ]

#     def format(self) -> str:
#         raise NotImplementedError()







#     """

    
    



        