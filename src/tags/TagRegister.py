



# class TagRegister:
#     """
#     uuids_basetags: dict[str, str] = {
#         'uuid1': 'fastqc',
#         'uuid2': 'fastqc',
#         'uuid3': 'fastqc',
#     }
#     basetags_uuids: dict[str, list[str]] = {
#         'fastqc': ['uuid1', 'uuid2']
#     }
#     """
#     def __init__(self):
#         self.uuids_basetags: dict[str, str] = {}
#         self.basetags_uuids: dict[str, list[str]] = {}
        
#     def exists(self, uuid: str) -> bool:
#         if uuid in self.uuids_basetags:
#             return True
#         return False
    
#     def add(self, basetag: str, uuid: str) -> None:
#         self.uuids_basetags[uuid] = basetag
#         if basetag not in self.basetags_uuids:
#             self.basetags_uuids[basetag] = []
#         self.basetags_uuids[basetag].append(uuid)

#     def get(self, uuid: str) -> str:
#         basetag = self.uuids_basetags[uuid]
#         return self.format_basetag(basetag, uuid)
   
#     def get_base_tag(self, uuid: str) -> str:
#         return self.uuids_basetags[uuid]

#     def format_basetag(self, basetag: str, query_uuid: str) -> str:
#         stored_uuids = self.basetags_uuids[basetag]
#         if len(stored_uuids) <= 1:
#             return basetag # only 1 object using this basetag
#         for i, uuid in enumerate(stored_uuids):
#             if uuid == query_uuid:
#                 return f'{basetag}{i+1}' # appends '1', '2' etc if basetag is shared by multiple objects
#         raise RuntimeError(f'no tag registered for {query_uuid}')

#     # def to_dict(self) -> dict[str, Any]:
#     #     """for external writing to file"""
#     #     return {
#     #         'uuids_basetags': self.uuids_basetags,
#     #         'basetags_uuids': self.basetags_uuids,
#     #     }