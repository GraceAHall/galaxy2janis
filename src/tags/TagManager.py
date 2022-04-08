

from .FormattingStrategy import TaggableEntity, format_tag


class TagManager:
    permitted_entities: set[str]

    def __init__(self):
        self.uuids_basetags: dict[str, str] = {}
        self.basetags_uuids: dict[str, list[str]] = {}

    def exists(self, uuid: str) -> bool:
        if uuid in self.uuids_basetags:
            return True
        return False

    def register(self, tag_type: str, entity: TaggableEntity) -> None:
        if tag_type not in self.permitted_entities:
            raise RuntimeError(f'cannot register a {tag_type}')

        basetag = format_tag(tag_type, entity)
        uuid = entity.get_uuid()

        self.uuids_basetags[uuid] = basetag
        if basetag not in self.basetags_uuids:
            self.basetags_uuids[basetag] = []
        self.basetags_uuids[basetag].append(uuid)

    # def register_old(self, tag_type: str, uuid: str, entity_info: dict[str, str]) -> None:
    #     if tag_type not in self.permitted_entities:
    #         raise RuntimeError(f'cannot register a {tag_type}')
    #     basetag = TagFormatter().format(tag_type, entity_info)
    #     self.uuids_basetags[uuid] = basetag
    #     if basetag not in self.basetags_uuids:
    #         self.basetags_uuids[basetag] = []
    #     self.basetags_uuids[basetag].append(uuid)

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


class ToolTagManager(TagManager):
    permitted_entities: set[str] = set(
        ['tool', 'tool_input', 'tool_output']
    )

class WorkflowTagManager(TagManager):
    permitted_entities: set[str] = set(
        ['workflow', 'workflow_step', 'workflow_input_data_step', 'workflow_input', 'workflow_output']
    )






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




