


from command.components.inputs.Flag import Flag
from workflows.workflow.Workflow import Workflow
from command.components.CommandComponent import CommandComponent
from workflows.step.values.InputValue import InputValue
from workflows.step.inputs.StepInput import (
    ConnectionStepInput, 
    RuntimeStepInput, 
    StaticStepInput, 
    StepInput
)
from workflows.step.values.LinkingStrategy import (
    ConnectionLinkingStrategy, 
    RuntimeLinkingStrategy, 
    StaticValueLinkingStrategy, 
    DefaultValueLinkingStrategy,
    LinkingStrategy
)


class InputValueFactory:

    def create(self, component: CommandComponent, step_input: StepInput, workflow: Workflow) -> InputValue:
        strategy = self.select_strategy(component, step_input, workflow)
        value = strategy.link()
        return value

    def create_default(self, component: CommandComponent) -> InputValue:
        strategy = DefaultValueLinkingStrategy(component)
        value = strategy.link()
        return value
    
    def create_runtime(self, component: CommandComponent) -> InputValue:
        strategy = RuntimeLinkingStrategy(component)
        value = strategy.link()
        return value

    def create_unlinked_connection(self, step_input: ConnectionStepInput, workflow: Workflow) -> InputValue:
        component = Flag(prefix='__UNKNOWN__')
        strategy = ConnectionLinkingStrategy(component, step_input, workflow)
        value = strategy.link()
        return value


    def select_strategy(self, component: CommandComponent, step_input: StepInput, workflow: Workflow) -> LinkingStrategy:
        if step_input:
            match step_input:
                case ConnectionStepInput():
                    return ConnectionLinkingStrategy(component, step_input, workflow)
                case RuntimeStepInput():
                    return RuntimeLinkingStrategy(component) 
                case StaticStepInput():
                    return StaticValueLinkingStrategy(component, step_input)
                case _:
                    pass
        raise RuntimeError(f'cannot find galaxy step input for gxparam {step_input.name}')




