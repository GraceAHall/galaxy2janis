



# from abc import ABC, abstractmethod
# from typing import Any
# from command.components.CommandComponent import CommandComponent
# from command.components.inputs.Flag import Flag
# from command.components.inputs.Option import Option
# from command.components.inputs.Positional import Positional
# from tags.TagManager import TagManager
# from tool.Tool import Tool
# from workflows.io.WorkflowInput import WorkflowInput
# from workflows.io.WorkflowOutput import WorkflowOutput
# from workflows.step.Step import GalaxyWorkflowStep
# from workflows.workflow.Workflow import Workflow


# class GetStrategy(ABC):
#     @abstractmethod
#     def get(self, entity: Any) -> str:
#         ...

# class GenericGetStrategy(GetStrategy):
#     def __init__(self, tag_type: str):
#         self.tag_type = tag_type

#     def get(self, entity: Any) -> str:
#         return TagManager().get(
#             tag_type=self.tag_type,
#             uuid=entity.get_uuid()
#         )

# def select_get_strategy(entity: Any) -> GetStrategy:
#     match entity:
#         case Tool():
#             return GenericGetStrategy('tool_name')
#         case Positional() | Flag() | Option():
#             return GenericGetStrategy('tool_input')
#         case CommandComponent():
#             return GenericGetStrategy('tool_output')
#         case Workflow():
#             return GenericGetStrategy('workflow_name')
#         case GalaxyWorkflowStep():
#             return GenericGetStrategy('workflow_step')
#         case WorkflowInput():
#             return GenericGetStrategy('workflow_input')
#         case WorkflowOutput():
#             return GenericGetStrategy('workflow_output')
#         case _:
#             raise NotImplementedError()
