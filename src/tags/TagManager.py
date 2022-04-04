

from .TagRegister import TagRegister
from .TagFormatter import TagFormatter

# FILEPATHS = {
#     TagType.TOOL_NAME: 'runtimefiles/tool_name_tagregister.json',
#     TagType.TOOL_COMPONENT: 'runtimefiles/tool_component_tagregister.json',
#     TagType.WORKFLOW_NAME: 'runtimefiles/workflow_name_tagregister.json',
#     TagType.WORKFLOW_STEP: 'runtimefiles/workflow_step_tagregister.json',
#     TagType.WORKFLOW_INPUT: 'runtimefiles/workflow_input_tagregister.json', # includes runtime values
#     TagType.WORKFLOW_OUTPUT: 'runtimefiles/workflow_output_tagregister.json'
# }

# STR_TAGTYPE_MAP = {
#     'tool_name': TagType.TOOL_NAME,
#     'tool_component': TagType.TOOL_COMPONENT,
#     'workflow_name': TagType.WORKFLOW_NAME,
#     'workflow_step': TagType.WORKFLOW_STEP,
#     'workflow_input': TagType.WORKFLOW_INPUT,
#     'workflow_output': TagType.WORKFLOW_OUTPUT
# }



class TagManager:
    def __init__(self):
        self.registers: dict[str, TagRegister] = {}

    def register(self, tag_type: str, uuid: str, entity_info: dict[str, str]) -> None:
        basetag = TagFormatter().format(entity_info)
        the_register = self.select_register(tag_type)
        the_register.add(basetag, uuid)

    def select_register(self, tag_type: str) -> TagRegister:
        return self.registers[tag_type]
    
    def get(self, tag_type: str, uuid: str) -> str:
        the_register = self.select_register(tag_type)
        return the_register.get(uuid)


class ToolTagManager(TagManager):
    def __init__(self):
        self.registers = {
            'tool_name': TagRegister(),
            'tool_component': TagRegister()
        }

class WorkflowTagManager(TagManager):
    def __init__(self):
        self.registers = {
            'tool_name': TagRegister(),
            'workflow_name': TagRegister(),
            'workflow_step': TagRegister(),
            'workflow_input': TagRegister(),
            'workflow_output': TagRegister()
        }






# class  :
#     def __init__(self):
#         self.tool_names = 
#         self.the_register: dict[str, Any] = {}

#     def register(self, tag_type: str, uuid: str, entity_info: dict[str, str]) -> None:
#         if tag_type not in self.the_register:
#             self.the_register[tag_type] = {''}
#         basetag = self._format(entity_info) 
#         tag_register = self._load(ttype)
#         tag_register.add(basetag, uuid)
#         self._save(ttype, tag_register)

#     def get(self, tag_type: str, uuid: str) -> str:
#         ttype = STR_TAGTYPE_MAP[tag_type]
#         tag_register = self._load(ttype)
#         return tag_register.get(uuid)



























#     def _load(self, ttype: TagType) -> TagRegister:
#         """loads a dict of tag information from disk"""
#         path = FILEPATHS[ttype]
#         with open(path, 'r') as fp:
#             data = json.load(fp)
#             if 'uuids_basetags' not in data:
#                 data['uuids_basetags'] = {}
#             if 'basetags_uuids' not in data:
#                 data['basetags_uuids'] = {}
#             return TagRegister(data)
    
#     def _save(self, ttype: TagType, register: TagRegister) -> None:
#         """saves a dict of tag information to disk"""
#         path = FILEPATHS[ttype]
#         with open(path, 'w') as fp:
#             data = register.to_dict()
#             return json.dump(data, fp)




