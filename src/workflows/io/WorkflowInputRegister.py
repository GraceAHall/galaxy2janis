

# from typing import Tuple
# from tags.TagRegister import TagRegister
# from workflows.io.WorkflowInput import WorkflowInput


# class WorkflowInputRegister:
#     def __init__(self):
#         self.tags: TagRegister = TagRegister()
#         self.inputs: dict[str, WorkflowInput] = {}

#     def get(self, uuid: str) -> Tuple[str, WorkflowInput]:
#         return self.tags.get(uuid), self.inputs[uuid]

#     def get_inputs_for_step(self, step_id: int) -> dict[str, WorkflowInput]:
#         out: dict[str, WorkflowInput] = {}
#         for uuid, inp in self.inputs.items():
#             if inp.step_id == step_id:
#                 out[self.tags.get(uuid)] = inp
#         return out

#     def add(self, inp: WorkflowInput) -> None:
#         self.register_tag(inp)
#         self.register_input(inp)

#     def register_tag(self, inp: WorkflowInput) -> None:
#         if inp.is_galaxy_input_step:
#             name = inp.step_tag
#         else:
#             name = f'{inp.step_tag}_{inp.step_input}'
#         self.tags.add(
#             uuid=inp.get_uuid(),
#             entity_info={'name': name}
#         )

#     def register_input(self, inp: WorkflowInput) -> None:
#         self.inputs[inp.get_uuid()] = inp



