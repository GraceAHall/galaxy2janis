

from entities.workflow.input import WorkflowInput
import logs.logging as logging
from typing import Any, Optional

from shellparser.components.inputs.Flag import Flag
from shellparser.components.inputs.Option import Option

from entities.workflow import Workflow
from entities.workflow import WorkflowStep

from gx.gxtool.load import load_xmltool

from shellparser.cheetah.evaluation import sectional_evaluate
from shellparser.text.simplification.aliases import resolve_aliases
from shellparser.cmdstr.cmdstr import gen_command_string
from shellparser.text.load import load_xml_command_cheetah_eval

from ..factory import main as factory
from .ValueLinker import ValueLinker

from .. import utils as value_utils
from shellparser.text.regex import utils as regex_utils

import tags
import datatypes


class CheetahValueLinker(ValueLinker):
    """
    links values (and presence of bool tool inputs) using the patially 
    evaluated cheetah <command> section. 
    updates knowledge of components (mainly optionality). 
    """

    def __init__(self, step: WorkflowStep, workflow: Workflow):
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
        # how does this even work? 
        # $ can also mean env var? 
        if text:
            if text[0] == '$':
                return True
            elif len(text) > 1 and text[1] == '$':  # WTF 
                return True
        return False

    def handle_not_present_flag(self, flag: Flag) -> None:
        self.update_tool_values_static(component=flag, value=False)

    def handle_not_present_opt(self, option: Option) -> None:
        self.update_tool_values_static(component=option, value=None)
    
    def handle_gxvar_opt(self, option: Option, value: str) -> None:
        # TODO future: attach the identified param if not attached? 
        # should always be attached tho? 
        pass
    
    def handle_envvar_opt(self, option: Option, value: Any) -> None:
        self.update_tool_values_runtime(component=option)
    
    def handle_value_opt(self, option: Option, value: Any) -> None:
        self.update_tool_values_static(component=option, value=value)

    def update_tool_values_static(self, component: Flag | Option, value: Any) -> None:
        # create value
        is_default = True if component.default_value == value else False
        inputval = factory.static(component, value, default=is_default)
        # add to register
        register = self.step.tool_values
        register.update_linked(component.uuid, inputval)
    
    def update_tool_values_runtime(self, component: Flag | Option) -> None:
        # create & add new workflow input
        winp = self.create_workflow_input(component)
        self.workflow.add_input(winp)
        # create value
        inputval = factory.workflow_input(component, winp, is_runtime=True)
        # add to register
        register = self.step.tool_values
        register.update_linked(component.uuid, inputval)

    def create_workflow_input(self, component: Flag | Option) -> WorkflowInput:
        """creates a workflow input for the tool input component"""
        return WorkflowInput(
            name=tags.tool.get(component.uuid),
            array=component.array,
            is_galaxy_input_step=False,
            janis_datatypes=datatypes.get(component),
        )



