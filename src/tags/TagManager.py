
import json

from .TagType import TagType
from .TagRegister import TagRegister
from .TagFormatter import TagFormatter

FILEPATHS = {
    TagType.TOOL_NAME: 'runtimefiles/tool_name_tagregister.json',
    TagType.TOOL_COMPONENT: 'runtimefiles/tool_component_tagregister.json',
    TagType.WORKFLOW_STEP: 'runtimefiles/workflow_step_tagregister.json',
    TagType.WORKFLOW_INPUT: 'runtimefiles/workflow_input_tagregister.json', # includes runtime values
    TagType.WORKFLOW_OUTPUT: 'runtimefiles/workflow_output_tagregister.json'
}

STR_TAGTYPE_MAP = {
    'tool_name': TagType.TOOL_NAME,
    'tool_component': TagType.TOOL_COMPONENT,
    'workflow_step': TagType.WORKFLOW_STEP,
    'workflow_input': TagType.WORKFLOW_INPUT,
    'workflow_output': TagType.WORKFLOW_OUTPUT
}


class TagManager:

    def register(self, tag_type: str, uuid: str, entity_info: dict[str, str]) -> None:
        ttype = STR_TAGTYPE_MAP[tag_type]
        basetag = self._format(entity_info) 
        tag_register = self._load(ttype)
        tag_register.add(basetag, uuid)
        self._save(ttype, tag_register)

    def get(self, tag_type: str, uuid: str) -> str:
        ttype = STR_TAGTYPE_MAP[tag_type]
        tag_register = self._load(ttype)
        return tag_register.get(uuid)

    def _format(self, entity_info: dict[str, str]) -> str:
        return TagFormatter().format(entity_info)
    
    def _load(self, ttype: TagType) -> TagRegister:
        """loads a dict of tag information from disk"""
        path = FILEPATHS[ttype]
        with open(path, 'r') as fp:
            data = json.load(fp)
            return TagRegister(data)
    
    def _save(self, ttype: TagType, register: TagRegister) -> None:
        """saves a dict of tag information to disk"""
        path = FILEPATHS[ttype]
        with open(path, 'w') as fp:
            data = register.to_dict()
            return json.dump(data, fp)




