

from typing import Any

from command.components.CommandComponent import CommandComponent
from .FormattingStrategy import format_tag


def get_tool_input_name(component: CommandComponent) -> str:
    default_name = component.get_name()
    if default_name.isnumeric() and component.gxparam:
        return component.gxparam.name.rsplit('.', 1)[-1]
    return default_name



class TagManager:
    permitted_entities: set[str]

    def __init__(self):
        self.uuids_basetags: dict[str, str] = {}
        self.basetags_uuids: dict[str, list[str]] = {}

    def uuid_exists(self, uuid: str) -> bool:
        if uuid in self.uuids_basetags:
            return True
        return False

    def register(self, tag_type: str, entity: Any) -> None:
        if tag_type not in self.permitted_entities:
            raise RuntimeError(f'cannot register a {tag_type}')

        starting_text = self._get_starting_text(tag_type, entity)
        basetag = format_tag(starting_text, tag_type, entity)
        uuid = entity.get_uuid()

        self.uuids_basetags[uuid] = basetag
        if basetag not in self.basetags_uuids:
            self.basetags_uuids[basetag] = []
        self.basetags_uuids[basetag].append(uuid)

    def get(self, uuid: str) -> str:
        basetag = self.uuids_basetags[uuid]
        return self._format_basetag(basetag, uuid)
    
    def get_base_tag(self, uuid: str) -> str:
        return self.uuids_basetags[uuid]

    def _format_basetag(self, basetag: str, query_uuid: str) -> str:
        stored_uuids = self.basetags_uuids[basetag]
        if len(stored_uuids) <= 1:
            return basetag # only 1 object using this basetag
        for i, uuid in enumerate(stored_uuids):
            if uuid == query_uuid:
                return f'{basetag}{i+1}' # appends '1', '2' etc if basetag is shared by multiple objects
        raise RuntimeError(f'no tag registered for {query_uuid}')

    def _get_starting_text(self, entity_type: str, entity: Any) -> str:
        match entity_type:
            case 'workflow':
                return entity.metadata.name # type: ignore
            case 'workflow_input':
                if entity.is_galaxy_input_step: # type: ignore
                    return f'in_{entity.name}' # type: ignore
                else:
                    return f'{entity.step_tag}_{entity.name}' # type: ignore
            case 'workflow_step':
                return entity.metadata.tool_id # type: ignore
            case 'workflow_output':
                return f'{entity.step_tag}_{entity.toolout_tag}' # type: ignore
            case 'tool':
                return entity.metadata.id # type: ignore
            case 'tool_input':
                return get_tool_input_name(entity)
            case 'tool_output':
                basetag = entity.get_name()
                if basetag.startswith('out_') and basetag not in self.basetags_uuids:
                    return basetag
                else:
                    return f'out_{basetag}'
            case _:
                raise RuntimeError()

    def _generate_all_tags(self) -> set[str]:
        tags: set[str] = set()
        for basetag, uuid_list in self.basetags_uuids.items():
            if len(uuid_list) == 1:
                tags.add(basetag)
            else:
                for i in range(len(uuid_list)):
                    tags.add(f'{basetag}{i+1}')
        return tags



class ToolTagManager(TagManager):
    permitted_entities: set[str] = set(
        ['tool', 'tool_input', 'tool_output']
    )

class WorkflowTagManager(TagManager):
    permitted_entities: set[str] = set(
        ['workflow', 'workflow_input', 'workflow_step', 'workflow_output']
    )



    
    # def tag_exists(self, tag: str) -> bool:
    #     all_tags = self._generate_all_tags()
    #     if tag in all_tags:
    #         return True
    #     return False

    # def register_old(self, tag_type: str, uuid: str, entity_info: dict[str, str]) -> None:
    #     if tag_type not in self.permitted_entities:
    #         raise RuntimeError(f'cannot register a {tag_type}')
    #     basetag = TagFormatter().format(tag_type, entity_info)
    #     self.uuids_basetags[uuid] = basetag
    #     if basetag not in self.basetags_uuids:
    #         self.basetags_uuids[basetag] = []
    #     self.basetags_uuids[basetag].append(uuid)

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




