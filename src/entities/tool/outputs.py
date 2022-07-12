

import logs.logging as logging

from shellparser.Command import Command
from shellparser.components.inputs.Flag import Flag
from shellparser.components.outputs.RedirectOutput import RedirectOutput
from shellparser.components.outputs.create import create_output
from shellparser.components.CommandComponent import CommandComponent

from gx.gxtool.XMLToolDefinition import XMLToolDefinition
from gx.gxtool.param.Param import Param
    

def extract_outputs(xmltool: XMLToolDefinition, command: Command) -> list[CommandComponent]:
    extractor = OutputExtractor(xmltool, command)
    return extractor.extract()


class OutputExtractor:
    def __init__(self, xmltool: XMLToolDefinition, command: Command):
        self.xmltool = xmltool
        self.command = command

    def extract(self) -> list[CommandComponent]:
        outputs: list[CommandComponent] = []
        outputs += self.get_redirect_outputs()
        outputs += self.get_input_outputs()
        outputs += self.get_wildcard_outputs()
        outputs += self.get_uncertain_outputs(outputs)
        return outputs
        
    def get_redirect_outputs(self) -> list[CommandComponent]:
        # redirect outputs (stdout) already identified when creating Command()
        # need to ensure they're linked to a gxparam
        # if not, try to link to dataset collector, else just ignore as the 
        # redirect seems to be dropped.
        out: list[CommandComponent] = []
        redirects: list[RedirectOutput] = self.command.list_outputs()
        for r in redirects:
            self.attempt_redirect_gxparam_link(r)
            if r.gxparam is not None:
                out.append(r)
        return out

    def attempt_redirect_gxparam_link(self, r: RedirectOutput) -> None:
        if not r.gxparam:
            for query_param in self.xmltool.list_outputs():
                if query_param.wildcard_pattern is not None:
                    if query_param.wildcard_pattern == r.file_token.text:
                        r.gxparam = query_param

    def get_input_outputs(self) -> list[CommandComponent]:
        # can be identified by looking at the input components which
        # have attached gxparams which are outputs. 
        # example case: toolname input.fastq -o $outfile
        # the -o option would be picked up as a command component, and the
        # gxparam referred to by $outfile is stored on the command component
        out: list[CommandComponent] = []
        for component in self.command.list_inputs(include_base_cmd=False):
            if self.should_create_input_output(component):
                out.append(create_output('input', component))
        return out
    
    def get_wildcard_outputs(self) -> list[CommandComponent]:
        # verified vs unverified:
        # only if no post-processing! otherwise, wildcard outputs may 
        # have come from post-processing.
        
        # outputs which were not identified in the command
        # usually just because they have a file collection strategy
        # like from_work_dir or a <discover_datatsets> tag as a child
        out: list[CommandComponent] = []
        for gxparam in self.xmltool.list_outputs():
            if self.should_create_wildcard_output(gxparam):
                out.append(create_output('wildcard', gxparam))
        return out

    def get_uncertain_outputs(self, existing_outputs: list[CommandComponent]) -> list[CommandComponent]:
        out: list[CommandComponent] = []
        for gxparam in self.xmltool.list_outputs():
            if self.should_create_uncertain_output(gxparam, existing_outputs):
                logging.uncertain_output()
                out.append(create_output('uncertain', gxparam))
        return out

    # CHECKS
    def should_create_input_output(self, component: CommandComponent) -> bool:
        if not isinstance(component, Flag):
            if component.gxparam and self.xmltool.outputs.get(component.gxparam.name):
                return True
        return False

    def should_create_wildcard_output(self, gxparam: Param) -> bool:
        """test to see if this *galaxy output param* should spawn WildcardOutput"""
        # UNCOMMENT THIS TO MAKE STRICT
        # if len(self.command.xmlcmdstr.postprocessing) == 0:
        if hasattr(gxparam, 'wildcard_pattern') and gxparam.wildcard_pattern is not None: # type: ignore
            if not self.command.gxparam_is_attached(gxparam): 
                return True
        return False

    def should_create_uncertain_output(self, gxparam: Param, existing_outputs: list[CommandComponent]) -> bool:
        """
        test to see if this *galaxy output param* should spawn UncertainOutput
        all galaxy outputs which are not yet accounted for must become UncertainOutputs
        """
        has_output_component = False
        for output in existing_outputs:
            if output.gxparam and output.gxparam.name == gxparam.name:
                has_output_component = True
                break
        if not has_output_component:
            return True
        return False

    def verify_outputs(self, outputs: list[CommandComponent]) -> None:
        # just checks we have the same number of outputs identified as CommandComponents
        # as there are in the xmltool's listed output params
        assert(len(self.xmltool.list_outputs()) == len(outputs))