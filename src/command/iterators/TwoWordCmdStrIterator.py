

from typing import Iterable, Tuple
from command.cmdstr.ToolExecutionSource import ToolExecutionSource
from command.tokens.Tokens import Token

class TwoWordCmdStrIterator:
    """
    iterates through a ToolExecutionSource, yielding the current tokens being assessed.
    keeps track of the location we are in the ToolExecutionSource

    Example ToolExecutionSource:
    fastqc --in1 input1.fastq --mode fast report.txt ...
    
    0           1             2             3           4           5
    fastqc      --in1         input1.fastq  --mode      fast        report.txt 
    RAW_STRING  RAW_STRING    RAW_STRING    RAW_STRING  RAW_STRING  RAW_STRING

    at token 1, we would return {
        ctoken: token 1  (--in1's token),
        ntokens: [token 2]
    }
    at token 3, we would return {
        ctoken: token 3 (--mode's token),
        ntokens: [token 4]
    }
    
    at token 3, GreedyCmdStrIterator would have returned {
        ctoken: token 3 (--mode's token),
        ntokens: [token 4, token 5]
    }
    """

    def iter(self, cmdstr: ToolExecutionSource) -> Iterable[Tuple[Token, list[Token]]]:
        raise NotImplementedError

    # def next(self, cmdstmt: CommandStatement, disallow: list[type[CommandComponent]]=[]) -> None:
    #     """
    #     iterate through command words (with next word for context)
    #     each pair of words may actually yield more than one component.
    #     see emboss_pepinfo.xml - has option value="-generalplot yes -hydropathyplot no"
    #     it is usually a single component though. only when is galaxy param.
    #     """
    #     cmdstr_components: list[CommandComponent] = []
    #     i = 0
    #     while i < len(cmdstmt.cmdwords) - 1:
    #         cword = cmdstmt.cmdwords[i]
    #         nword = cmdstmt.cmdwords[i + 1]
    #         components = self.component_factory.create(cword, nword)
    #         components = self.refine_components(components)
    #         self.iter_context.update(components, referrer=self)
    #         components = self.filter_components(components, disallow=disallow)
    #         components = self.annotate_iter_attrs(components)
    #         cmdstr_components += components
    #         i += self.iter_context.step_size
    #     self.update_command(cmdstr_components)