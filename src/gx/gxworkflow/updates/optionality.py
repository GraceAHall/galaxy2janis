


from entities.workflow import Workflow
from entities.workflow.step.inputs import InputValue, StaticInputValue


def update_components_optionality(invalue: InputValue, janis: Workflow) -> None:
    if invalue.component:
        if isinstance(invalue, StaticInputValue) and invalue.is_none:
            invalue.component.forced_optionality = True
        # check this updates the component in the Tool