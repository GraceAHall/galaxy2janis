


from .ValueLinker import ValueLinker
from factory import main as factory


class DefaultValueLinker(ValueLinker):

    def link(self) -> None:
        register = self.step.tool_values
        for component in self.get_linkable_components():
            input_value = factory.static(component, component.default_value, default=True)
            register.update_linked(component.uuid, input_value)

