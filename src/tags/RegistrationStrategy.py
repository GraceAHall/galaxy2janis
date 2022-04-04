


# from abc import ABC, abstractmethod
# from typing import Any
# from command.components.CommandComponent import CommandComponent
# from tags.TagManager import TagManager
# from tool.Tool import Tool
# from workflows.io.Input import WorkflowInput
# from workflows.io.Output import WorkflowOutput
# from workflows.step.Step import GalaxyWorkflowStep
# from workflows.workflow.Workflow import Workflow


# class RegistrationStrategy(ABC):
#     @abstractmethod
#     def register(self, entity: Any) -> None:
#         ...

# class ToolNameRegistrationStrategy(RegistrationStrategy):
#     def register(self, entity: Tool) -> None:
#         TagManager().register(
#             tag_type='tool_name',
#             uuid=entity.get_uuid(),
#             entity_info={'name': entity.metadata.id}
#         )

# class ToolComponentRegistrationStrategy(RegistrationStrategy):
#     def register(self, entity: CommandComponent) -> None:
#         TagManager().register(
#             tag_type='tool_component',
#             uuid=entity.get_uuid(),
#             entity_info={
#                 'name': entity.get_name(),
#                 'datatype': entity.janis_datatypes[0].classname
#             }
#         )

# class WorkflowNameRegistrationStrategy(RegistrationStrategy):
#     def register(self, entity: Workflow) -> None:
#         TagManager().register(
#             tag_type='workflow_name',
#             uuid=entity.get_uuid(),
#             entity_info={'name': entity.metadata.name}
#         )

# class WorkflowStepRegistrationStrategy(RegistrationStrategy):
#     def register(self, entity: GalaxyWorkflowStep) -> None:
#         TagManager().register(
#             tag_type='workflow_name',
#             uuid=entity.get_uuid(),
#             entity_info={'name': entity.metadata.step_name}
#         )

# class WorkflowInputRegistrationStrategy(RegistrationStrategy):
#     def register(self, entity: WorkflowInput) -> None:
#         TagManager().register(
#             tag_type='workflow_input',
#             uuid=entity.get_uuid(),
#             entity_info={'name': f'{entity.step_name}_{entity.step_input}'}
#         )

# class WorkflowOutputRegistrationStrategy(RegistrationStrategy):
#     def register(self, entity: WorkflowOutput) -> None:
#         TagManager().register(
#             tag_type='workflow_output',
#             uuid=entity.get_uuid(),
#             entity_info={'name': f'{entity.source_tag}_{entity.source_output}'}
#         )


# def select_registration_strategy(entity: Any) -> RegistrationStrategy:
#     match entity:
#         case Tool():
#             return ToolNameRegistrationStrategy()
#         case CommandComponent():
#             return ToolComponentRegistrationStrategy()
#         case Workflow():
#             return WorkflowNameRegistrationStrategy()
#         case GalaxyWorkflowStep():
#             return WorkflowStepRegistrationStrategy()
#         case WorkflowInput():
#             return WorkflowInputRegistrationStrategy()
#         case WorkflowOutput():
#             return WorkflowOutputRegistrationStrategy()
#         case _:
#             raise NotImplementedError()
