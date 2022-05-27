

from typing import Any
from .FormattingStrategy import format_tag



class TagManager:
    permitted_entities: set[str]

    def __init__(self):
        self.uuids_basetags: dict[str, str] = {}
        self.basetags_uuids: dict[str, list[str]] = {}

    def exists(self, uuid: str) -> bool:
        if uuid in self.uuids_basetags:
            return True
        return False
    
    def get(self, uuid: str) -> str:
        basetag = self.uuids_basetags[uuid]
        return self._format_basetag(basetag, uuid)
    
    def get_base_tag(self, uuid: str) -> str:
        return self.uuids_basetags[uuid]

    def register(self, tag_type: str, entity: Any) -> None:
        if tag_type not in self.permitted_entities:
            raise RuntimeError(f'cannot register a {tag_type}')

        #starting_text = self._get_starting_text(tag_type, entity)
        basetag = format_tag(tag_type, entity)
        uuid = entity.uuid

        self.uuids_basetags[uuid] = basetag
        if basetag not in self.basetags_uuids:
            self.basetags_uuids[basetag] = []
        self.basetags_uuids[basetag].append(uuid)

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
        ['workflow', 'workflow_input', 'workflow_step', 'workflow_output']
    )



    # def _generate_all_tags(self) -> set[str]:
    #     tags: set[str] = set()
    #     for basetag, uuid_list in self.basetags_uuids.items():
    #         if len(uuid_list) == 1:
    #             tags.add(basetag)
    #         else:
    #             for i in range(len(uuid_list)):
    #                 tags.add(f'{basetag}{i+1}')
    #     return tags


