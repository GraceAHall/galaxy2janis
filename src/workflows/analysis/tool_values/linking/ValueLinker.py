

import logs.logging as logging
from abc import ABC, abstractmethod
from typing import Any, Iterable, Optional

import settings
from shellparser.components.CommandComponent import CommandComponent
from shellparser.components.inputs.Flag import Flag
from shellparser.components.inputs.Option import Option

from entities.workflow import Workflow
from entities.workflow import WorkflowStep
from entities.workflow import ConnectionStepInput, StepInput, WorkflowInputStepInput
from entities.workflow import InputValue

from shellparser.cheetah.evaluation import sectional_evaluate
from shellparser.text.simplification.aliases import resolve_aliases
from gx.xmltool.load import load_xmltool
from shellparser.cmdstr.cmdstr import gen_command_string

from shellparser.text.load import load_xml_command_cheetah_eval
import workflows.analysis.tool_values.create_value as value_factory
import workflows.analysis.tool_values.utils as value_utils
import shellparser.text.regex.utils as regex_utils


class ValueLinker(ABC):
    """
    assigns values to each tool argument given some reference information
    
    InputDictValueLinker looks up values directly from the step input dict
    when possible (a gxparam is attached to the component)

    CheetahValueLinker follows similar logic to InputDictValueLinker, except also 
    templates the <command> with the step input dict, then uses the templated <command> 
    to locate arguments and pull their value
    """
    def __init__(self, step: WorkflowStep, workflow: Workflow):
        self.step = step
        self.workflow = workflow

    @abstractmethod
    def link(self) -> None:
        """links tool arguments to their value for a given workflow step"""
        ...

    def get_linkable_components(self) -> list[CommandComponent]:
        out: list[CommandComponent] = []
        # check to see if its already linked, if so, ignore, else link
        for component in self.step.tool.list_inputs():
            if not self.step.tool_values.get(component.uuid):
                out.append(component)
        return out

    def mark_linked(self, incoming: Any) -> None:
        if hasattr(incoming, 'gxparam') and incoming.gxparam is not None:
            for step_input in self.step.inputs.list():
                if step_input.gxparam is not None:
                    if step_input.gxparam.name == incoming.gxparam.name:
                        step_input.linked = True


class CheetahValueLinker(ValueLinker):
    """
    links values (and presence of bool tool inputs) using the patially 
    evaluated cheetah <command> section. 
    updates knowledge of components (mainly optionality). 
    """

    def __init__(selfstep: WorkflowStep, workflow: Workflow):
        super().__init__(step, workflow)
        self.cmdstr: str = self.prepare_command()

    def prepare_command(self) -> str:
        text = load_xml_command_cheetah_eval()
        text = sectional_evaluate(text, inputs=self.step.inputs.to_dict())
        text = resolve_aliases(text)

        xmltool = load_xmltool()
        cmdstr = gen_command_string(source='xml', the_string=text, xmltool=xmltool)
        stmtstr = cmdstr.main.cmdline
        
        logging.runtime_data(text)
        logging.runtime_data(stmtstr)
        
        return stmtstr

    def link(self) -> None:
        for component in self.get_linkable_components():
            match component:
                case Flag():
                    self.link_flag(component)
                case Option():
                    self.link_option(component)
                case _:
                    pass
    
    def link_flag(self, flag: Flag) -> None:
        """
        links a flag component value as None if not in cmdstr
        should only detect the flag's absense, nothing else
        """
        if not regex_utils.word_exists(flag.prefix, self.cmdstr):
            self.handle_not_present_flag(flag)

    def link_option(self, option: Option) -> None:
        """gets the value for a specific tool argument"""
        value = regex_utils.get_next_word(option.prefix, option.delim, self.cmdstr)
        value = None if value == '' else value
        if value is None:
            self.handle_not_present_opt(option)
        elif self.is_param(value):
            self.handle_gxvar_opt(option, value)
        elif value_utils.is_env_var(value) or value_utils.has_env_var(value):
            self.handle_envvar_opt(option, value)
        else:
            self.handle_value_opt(option, value)

    # TODO upgrade for pre/post task section
    def is_param(self, text: Optional[str]) -> bool:
        if text:
            if text[0] == '$':
                return True
            elif len(text) > 1 and text[1] == '$':
                return True
        return False

    def handle_not_present_flag(self, flag: Flag) -> None:
        self.update_tool_values_static(component=flag, value=False)

    def handle_not_present_opt(self, option: Option) -> None:
        self.update_tool_values_static(component=option, value=None)
    
    def handle_gxvar_opt(self, option: Option, value: str) -> None:
        # future: attach the identified param if not attached? 
        # should always be attached tho? 
        pass
    
    def handle_envvar_opt(self, option: Option, value: Any) -> None:
        self.update_tool_values_runtime(component=option, value=value)
    
    def handle_value_opt(self, option: Option, value: Any) -> None:
        self.update_tool_values_static(component=option, value=value)

    def update_tool_values_static(self, component: Flag | Option, value: Any) -> None:
        register = self.step.tool_values
        inputval = value_factory.create_static(component, value)  # type: ignore
        register.update_linked(component.uuid, inputval)
        self.mark_linked(component)
    
    def update_tool_values_runtime(self, component: Flag | Option, value: Any) -> None:
        register = self.step.tool_values
        inputval = value_factory.create_runtime(component)  # type: ignore
        register.update_linked(component.uuid, inputval)
        self.mark_linked(component)




class InputDictValueLinker(ValueLinker):

    def link(self) -> None:
        # link tool components to static and connection inputs
        inp_register = self.step.inputs
        val_register = self.step.tool_values
        
        for component in self.get_linkable_components():
            if self.is_directly_linkable(component):
                gxvarname = component.gxparam.name  # type: ignore
                step_input = inp_register.get(gxvarname)

                if step_input:
                    value = value_factory.create(component, step_input, self.workflow)
                    val_register.update_linked(component.uuid, value)
                    self.mark_linked(step_input)
    
    def is_directly_linkable(self, component: CommandComponent) -> bool:
        """
        checks whether a janis tool input can actually be linked to a value in the 
        galaxy workflow step.
        only possible if the component has a gxparam, and that gxparam is referenced as a
        ConnectionStepInput, RuntimeStepInput or StaticStepInput
        """
        if component.gxparam:
            query = component.gxparam.name 
            if self.step.inputs.get(query):
                return True
        return False
    

class DefaultValueLinker(ValueLinker):

    def link(self) -> None:
        val_register = self.step.tool_values
        for component in self.get_linkable_components():
            value = value_factory.create_default(component)
            val_register.update_linked(component.uuid, value)


class UnlinkedValueLinker(ValueLinker):

    def __init__(self, step: WorkflowStep, workflow: Workflow):
        super().__init__(step, workflow)
        self.permitted_inputs = [WorkflowInputStepInput, ConnectionStepInput]

    def link(self) -> None:
        register = self.step.tool_values
        for step_input in self.get_unlinked():
            invalue = self.create_invalue(step_input)
            register.update_unlinked(invalue)
            logging.unlinked_input_connection()

    def get_unlinked(self) -> Iterable[StepInput]:
        for step_input in self.step.inputs.list():
            if not step_input.linked and type(step_input) in self.permitted_inputs:
                yield step_input

    def create_invalue(self, step_input: StepInput) -> InputValue:
        # workflow inputs (genuine or runtime)
        if isinstance(step_input, WorkflowInputStepInput):
            workflow_input = self.workflow.get_input(step_id=step_input.step_id)
            assert(workflow_input)
            return value_factory.create_unlinked_workflowinput(workflow_input)
        # step connections
        elif isinstance(step_input, ConnectionStepInput):
            return value_factory.create_unlinked_connection(step_input, self.workflow)
        else:
            raise RuntimeError()

